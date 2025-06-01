import json

from sqlalchemy import select

from database.models import AppSettings
from database.models.account import Account
from database.storage import Session
from oidc import KeycloakAdmin
from tasks.base import BaseTask


class SyncFromKeycloakTask(BaseTask):
    LABEL = "Kopiere Nutzer von Keycloak zur Datenbank"
    ON_STARTUP = True

    def run(self):
        self.progress = 0

        with Session() as session:
            admin = KeycloakAdmin()
            self.logger.info("Starting download…")
            res = admin.get_user_list(stream=True)

            total_size = res.headers.get("content-length")
            if total_size is None:
                total_size = (
                    session.execute(
                        select(AppSettings.value).filter(
                            AppSettings.key == "last_keycloak_content_length"
                        )
                    ).scalar_one_or_none()
                    or 0
                )

            total_size = int(total_size)
            if total_size == 0:
                self.progress = None
            block_size = 2048

            raw_response = b""
            for i, chunk in enumerate(res.iter_content(block_size)):
                if self.sig_killed:
                    raise Exception("Task was killed")
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
            last_total_size = session.execute(
                select(AppSettings).filter(
                    AppSettings.key == "last_keycloak_content_length"
                )
            ).scalar_one_or_none()
            if last_total_size is None:
                last_total_size = AppSettings(key="last_keycloak_content_length")
            last_total_size.value = str(len(raw_response))
            session.add(last_total_size)

            users = json.loads(raw_response)
            total_users = len(users)
            self.logger.info(f"Downloaded {total_users} user accounts")
            for i, user in enumerate(users):
                if self.sig_killed:
                    raise Exception("Task was killed")

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
                if notification_settings := user["attributes"].get(
                    "drink_notification"
                ):
                    account.summary_email_notification_setting = notification_settings[
                        0
                    ]
                self.progress = (i + 1) / total_users
            Session().commit()
            self.logger.info(f"Synced {total_users} users")

    def find_account_by_keycloak_id(self, keycloak_id) -> Account | None:
        if keycloak_id is None:
            return None
        self.logger.info(f"Looking for keycloak user {keycloak_id}")
        query = select(Account).where(Account.keycloak_sub == keycloak_id)
        with Session() as session:
            return session.scalars(query).one_or_none()

    def find_account_by_ldap_entry_dn(self, ldap_entry_dn) -> Account | None:
        if ldap_entry_dn is None:
            return None
        self.logger.info(f"Looking for ldap user {ldap_entry_dn}")
        query = select(Account).where(Account.ldap_path == ldap_entry_dn)
        with Session() as session:
            return session.scalars(query).one_or_none()

    def find_account_by_name(self, name) -> Account | None:
        if name is None:
            return None
        self.logger.info(f"Looking for username {name}")
        query = select(Account).where(Account.name == name)
        with Session() as session:
            return session.scalars(query).one_or_none()
