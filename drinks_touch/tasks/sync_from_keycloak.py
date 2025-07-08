import json

from database.models import AppSettings
from database.models.account import Account
from database.storage import Session, with_db
from oidc import KeycloakAdmin
from tasks.base import BaseTask


class SyncFromKeycloakTask(BaseTask):
    LABEL = "Kopiere Nutzer von Keycloak zur Datenbank"
    ON_STARTUP = True

    @with_db
    def run(self):
        self.progress = 0

        admin = KeycloakAdmin()
        self.logger.info("Starting download…")
        res = admin.get_user_list(stream=True)

        total_size = res.headers.get("content-length")
        if total_size is None:
            last_total_size = AppSettings.query.filter(
                AppSettings.key == "last_keycloak_content_length"
            ).one_or_none()
            if last_total_size is not None:
                total_size = last_total_size.value
            else:
                total_size = 0

        total_size = int(total_size)
        if total_size == 0:
            self.progress = None
        block_size = 2048

        raw_response = b""
        for i, chunk in enumerate(res.iter_content(block_size)):
            if self.sig_killed:
                self.logger.error("Task was killed while downloading users")
                self._fail()
                return
            raw_response += chunk
            self.logger.info(f"Downloaded {len(raw_response):6} bytes")
            if total_size:
                if total_size < len(raw_response):
                    # Last time, we downloaded less than this time.
                    # We don't know how much more we need to download.
                    # Show an indeterminate progress bar.
                    self.progress = None
                else:
                    self.progress = len(raw_response) / total_size

        # insert or update the last content length
        last_total_size = AppSettings.query.filter(
            AppSettings.key == "last_keycloak_content_length"
        ).one_or_none()
        if last_total_size is None:
            last_total_size = AppSettings(key="last_keycloak_content_length")
        last_total_size.value = str(len(raw_response))
        Session().add(last_total_size)

        users = json.loads(raw_response)
        total_users = len(users)
        self.logger.info(f"Downloaded {total_users} user accounts")
        for i, user in enumerate(users):
            if self.sig_killed:
                self.logger.error("Task was killed while saving users")
                self._fail()
                return

            ldap_entry_dn = user["attributes"].get("LDAP_ENTRY_DN", [None])[0]
            if account := self.find_account_by_keycloak_id(user["id"]):
                self.logger.info(f"Updating user {account.keycloak_sub}")
            elif account := self.find_account_by_ldap_entry_dn(ldap_entry_dn):
                self.logger.info(f"Updating ldap={account.ldap_path}")
            elif self.find_account_by_name(user["username"]):
                self.logger.error(
                    f"Account with name {user['username']} already exists, but it's neither linked to the "
                    f"keycloak id {user['id']} nor the ldap path {ldap_entry_dn}"
                )
                continue
            else:
                account = Account(
                    keycloak_sub=user["id"],
                    ldap_path=ldap_entry_dn,
                )
                Session.add(account)
                self.logger.info(
                    f"Creating user sub={account.keycloak_sub}, ldap_entry_dn={account.ldap_path}"
                )
            account.keycloak_sub = user["id"]
            account.name = user["username"]
            account.email = user.get("email")
            account.enabled = user["enabled"]
            if notification_settings := user["attributes"].get("drink_notification"):
                account.summary_email_notification_setting = notification_settings[0]
            self.progress = (i + 1) / total_users
        self.logger.info(f"Synced {total_users} users")

    def find_account_by_keycloak_id(self, keycloak_id) -> Account | None:
        if keycloak_id is None:
            return None
        self.logger.info(f"Looking for keycloak user {keycloak_id}")
        return Account.query.filter(Account.keycloak_sub == keycloak_id).one_or_none()

    def find_account_by_ldap_entry_dn(self, ldap_entry_dn) -> Account | None:
        if ldap_entry_dn is None:
            return None
        self.logger.info(f"Looking for ldap user {ldap_entry_dn}")
        return Account.query.filter(Account.ldap_path == ldap_entry_dn).one_or_none()

    def find_account_by_name(self, name) -> Account | None:
        if name is None:
            return None
        self.logger.info(f"Looking for username {name}")
        return Account.query.filter(Account.name == name).one_or_none()
