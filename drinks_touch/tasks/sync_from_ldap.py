from database.models.account import Account
from database.storage import Session
from tasks.base import BaseTask
import logging


logger = logging.getLogger(__name__)


class SyncFromLDAPTask(BaseTask):
    label = "Kopiere Nutzer von LDAP zur Datenbank"

    def run(self):
        def set_progress(progress):
            self.progress = progress

        self.progress = 0

        with Session.begin():
            Account.sync_all_from_ldap(progress=set_progress)
