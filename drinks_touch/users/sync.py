from datetime import datetime

import logging
from json import JSONDecodeError

import requests
from decimal import Decimal
from requests.auth import HTTPBasicAuth

import config
from database.models import Tx
from database.models.account import Account
from database.models.recharge_event import RechargeEvent
from database.storage import get_session, Session
from notifications.notification import send_summary

logger = logging.getLogger(__name__)

helper_user = "SEPA"


def get_existing(session):
    rechargeevents = (
        session.query(RechargeEvent)
        .filter(RechargeEvent.helper_user_id == str(helper_user))
        .all()
    )
    got_by_user = {}
    for ev in rechargeevents:
        if ev.user_id not in got_by_user:
            got_by_user[ev.user_id] = []
        got_by_user[ev.user_id].append(ev)
    return got_by_user


def sync_recharges():
    try:
        sync_recharges_real()
    except Exception:
        logger.exception("Syncing recharges:")


def sync_recharges_real():
    try:
        data = requests.get(
            config.MONEY_URL,
            auth=HTTPBasicAuth(config.MONEY_USER, config.MONEY_PASSWORD),
        )
        recharges = data.json()
    except requests.exceptions.ConnectionError:
        logger.exception("Cannot connect to sync recharges:")
        return
    except JSONDecodeError:
        logger.exception("Cannot decode sync recharge json:")
        return

    session = get_session()
    got_by_user = get_existing(session)

    for uid, charges in recharges.items():
        logger.info("Syncing recharges for user %s", uid)
        if uid not in got_by_user:
            logger.info("First recharge for user %s!", uid)
            got_by_user[uid] = []
        got = got_by_user[uid]
        for charge in charges:
            charge_date = datetime.strptime(charge["date"], "%Y-%m-%d")
            charge_amount = Decimal(charge["amount"])
            logger.debug("charge: %s, %s", charge, charge_date)
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

            handle_transferred(charge, charge_amount, charge_date, got, session, uid)


def handle_transferred(charge, charge_amount, charge_date, got, session, uid):
    logger.info(
        "User %s transferred %s on %s: %s", uid, charge_amount, charge_date, charge
    )
    account = Account.query.filter(Account.ldap_id == uid).one()
    transaktion = Tx(
        created_at=charge_date,
        payment_reference="Aufladung via SEPA",
        account_id=account.id,
        amount=charge_amount,
    )
    session.add(transaktion)
    session.commit()
    ev = RechargeEvent(
        uid, helper_user, charge_amount, charge_date, tx_id=transaktion.id
    )
    got.append(ev)
    session.add(ev)
    session.commit()
    try:
        account = Session().query(Account).filter(Account.ldap_id == uid).one()
        if not account:
            logger.error("could not find user %s to send email", uid)
        else:
            subject = "Aufladung EUR %s für %s" % (charge_amount, account.name)
            text = "Deine Aufladung über %s € am %s mit Text '%s' war erfolgreich." % (
                charge_amount,
                charge_date,
                charge["info"],
            )
            send_summary(account, subject=subject, force=True, prepend_text=text)
    except Exception:
        logger.exception("sending notification mail:")


if __name__ == "__main__":
    sync_recharges()
