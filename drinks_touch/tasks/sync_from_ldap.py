from database.models.account import Account
from database.storage import Session
from tasks.base import BaseTask


class SyncFromLDAPTask(BaseTask):
    label = "Kopiere Nutzer von LDAP zur Datenbank"

    def run(self):
        def set_progress(progress, *args, **kwargs):
            self.progress = progress

        self.progress = 0
        with Session.begin():
            Account.sync_all_from_ldap(callback=set_progress)
