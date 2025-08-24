from sqlalchemy import select

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
from database.storage import Session, with_db


class SepaSyncTask(BaseTask):
    LABEL = "SEPA Synchronisation"
    ON_STARTUP = True

    @with_db
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
            if uid not in got_by_user:
                self.logger.info("First recharge for user %s!", uid)
                got_by_user[uid] = []
            got = got_by_user[uid]
            query = select(Account).filter(Account.ldap_id == uid)
            account = Session().execute(query).scalar_one()

            # Convert and sort by "date" column, just to be sure the charges are processed in the right order.
            # If it's in the wrong order, the "last_sepa_deposit" check may prevent old deposits
            # from being processed.
            charges = [
                {
                    "uid": charge["uid"],
                    "amount": Decimal(charge["amount"]),
                    "date": datetime.strptime(charge["date"], "%Y-%m-%d").date(),
                    "legacy_charge_date": datetime.strptime(charge["date"], "%Y-%m-%d"),
                    "info": charge["info"],
                }
                for charge in charges
            ]

            for charge in sorted(charges, key=lambda x: x["date"]):
                if (
                    account.last_sepa_deposit
                    and charge["date"] <= account.last_sepa_deposit
                ):
                    self.logger.debug(
                        "Skip charge for user %s on %s, last SEPA deposit was on %s",
                        uid,
                        charge["date"],
                        account.last_sepa_deposit,
                    )
                    continue
                account.last_sepa_deposit = charge["date"]

                # Legacy check for existing transactions
                # In the future we will only rely on "last_sepa_deposit",
                # so we can remove the RechargeEvent table.
                #
                # Need to be kept in this PR, because the "account.last_sepa_deposit" timestamp
                # is not yet set. It will be set after the first deployment.
                found = False
                for exist in got:
                    if exist.timestamp != charge["legacy_charge_date"]:
                        continue
                    if exist.amount != charge["amount"]:
                        continue
                    # found a matching one
                    found = True
                    break
                if found:
                    continue

                self.logger.info(
                    "Aufladung vom %s, %s€ für %s",
                    charge["date"],
                    charge["amount"],
                    account.name,
                )
                self.handle_transferred(charge, got, uid, account)

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

    def handle_transferred(self, charge, got, uid, account: Account):
        session = Session()
        tx = Tx(
            created_at=charge["date"],
            payment_reference="Aufladung via SEPA",
            account_id=account.id,
            amount=charge["amount"],
        )
        session.add(tx)
        session.flush()
        ev = RechargeEvent(uid, "SEPA", charge["amount"], charge["date"], tx_id=tx.id)
        got.append(ev)
        session.add(ev)

        subject = "Aufladung EUR %s für %s" % (charge["amount"], account.name)
        text = "Deine Aufladung über %s€ am %s mit Text '%s' war erfolgreich." % (
            charge["amount"],
            charge["date"],
            charge["info"],
        )
        content_text = text  # TODO: use jinja template
        content_html = text  # TODO: use jinja template
        send_notification(
            account.email, subject, content_text, content_html, account.ldap_id
        )
        session.flush()
