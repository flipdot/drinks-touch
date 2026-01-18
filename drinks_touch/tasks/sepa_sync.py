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

        for uid, charges in recharges.items():
            if self.sig_killed:
                self._fail()
                break

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

                self.logger.info(
                    "Aufladung vom %s, %s€ für %s",
                    charge["date"],
                    charge["amount"],
                    account.name,
                )
                self.handle_transferred(charge, account)

    @with_db
    def handle_transferred(self, charge, account: Account):
        session = Session()
        tx = Tx(
            created_at=charge["date"],
            payment_reference="Aufladung via SEPA",
            account_id=account.id,
            amount=charge["amount"],
        )
        session.add(tx)

        subject = "Aufladung EUR %s für %s" % (charge["amount"], account.name)
        text = "Deine Aufladung über %s€ am %s mit Text '%s' war erfolgreich." % (
            charge["amount"],
            charge["date"],
            charge["info"],
        )
        content_text = text  # TODO: use jinja template
        content_html = text  # TODO: use jinja template
        send_notification(
            account.email,
            subject,
            content_text,
            content_html,
            account.ldap_id,
            blocking=True,
        )
