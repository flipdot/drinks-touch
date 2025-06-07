from notifications.notification import send_notification
from tasks.base import BaseTask

from datetime import datetime

from json import JSONDecodeError

import requests
from decimal import Decimal
from requests.auth import HTTPBasicAuth

import config
from database.models import Tx
from database.models.account import Account
from database.models.recharge_event import RechargeEvent
from database.storage import Session


class SepaSyncTask(BaseTask):
    LABEL = "SEPA Synchronisation"
    ON_STARTUP = True

    def run(self):
        try:
            data = requests.get(
                config.MONEY_URL,
                auth=HTTPBasicAuth(config.MONEY_USER, config.MONEY_PASSWORD),
            )
        except requests.exceptions.ConnectionError as e:
            raise Exception("Cannot connect to money server") from e
        try:
            recharges = data.json()
        except JSONDecodeError as e:
            raise Exception("Cannot decode JSON from money server") from e

        got_by_user = self.get_existing()

        for uid, charges in recharges.items():
            if self.sig_killed:
                self._fail()
                break
            self.logger.info("Syncing recharges for user %s", uid)
            if uid not in got_by_user:
                self.logger.info("First recharge for user %s!", uid)
                got_by_user[uid] = []
            got = got_by_user[uid]
            for charge in charges:
                charge_date = datetime.strptime(charge["date"], "%Y-%m-%d")
                charge_amount = Decimal(charge["amount"])
                self.logger.debug("charge: %s, %s", charge, charge_date)
                found = False
                for exist in got:
                    if exist.timestamp != charge_date:
                        continue
                    if exist.amount != charge_amount:
                        continue
                    # found a matching one
                    found = True
                    break
                if found:
                    continue

                self.handle_transferred(charge, charge_amount, charge_date, got, uid)
        Session().commit()

    def get_existing(self):
        rechargeevents = (
            Session()
            .query(RechargeEvent)
            .filter(RechargeEvent.helper_user_id == "SEPA")
            .all()
        )
        got_by_user = {}
        for ev in rechargeevents:
            if ev.user_id not in got_by_user:
                got_by_user[ev.user_id] = []
            got_by_user[ev.user_id].append(ev)
        return got_by_user

    def handle_transferred(self, charge, charge_amount, charge_date, got, uid):
        session = Session()
        self.logger.info(
            "User %s transferred %s on %s: %s", uid, charge_amount, charge_date, charge
        )
        account = Account.query.filter(Account.ldap_id == uid).one()
        tx = Tx(
            created_at=charge_date,
            payment_reference="Aufladung via SEPA",
            account_id=account.id,
            amount=charge_amount,
        )
        session.add(tx)
        session.flush()
        ev = RechargeEvent(uid, "SEPA", charge_amount, charge_date, tx_id=tx.id)
        got.append(ev)
        session.add(ev)
        account = Session().query(Account).filter(Account.ldap_id == uid).one()
        if not account:
            self.logger.error("could not find user %s to send email", uid)
        else:
            subject = "Aufladung EUR %s für %s" % (charge_amount, account.name)
            text = "Deine Aufladung über %s € am %s mit Text '%s' war erfolgreich." % (
                charge_amount,
                charge_date,
                charge["info"],
            )
            content_text = text  # TODO: use jinja template
            content_html = text  # TODO: use jinja template
            send_notification(
                account.email, subject, content_text, content_html, account.ldap_id
            )
        session.flush()
