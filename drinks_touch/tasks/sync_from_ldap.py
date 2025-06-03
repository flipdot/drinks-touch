from database.models.account import Account
from database.storage import Session
from tasks.base import BaseTask
import logging


logger = logging.getLogger(__name__)


class SyncFromLDAPTask(BaseTask):
    LABEL = "Kopiere Nutzer von LDAP zur Datenbank"
    ON_STARTUP = True

    def run(self):
        def set_progress(progress):
            self.progress = progress

        self.progress = 0

        with Session.begin():
            Account.sync_all_from_ldap(
                progress=set_progress, was_killed=lambda: self.sig_killed
            )
