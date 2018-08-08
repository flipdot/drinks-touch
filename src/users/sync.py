# coding=utf-8

import logging
from datetime import datetime
from decimal import Decimal

import requests
from requests.auth import HTTPBasicAuth

import config
from database.models.recharge_event import RechargeEvent
from database.storage import get_session
from notifications.notification import send_summary_now
from users import Users

log = logging.getLogger(__name__)

helper_user = "SEPA"

def get_existing(session):
    rechargeevents = session.query(RechargeEvent) \
        .filter(RechargeEvent.helper_user_id == str(helper_user)).all()
    got_by_user = {}
    for ev in rechargeevents:
        if ev.user_id not in got_by_user:
            got_by_user[ev.user_id] = []
        got_by_user[ev.user_id].append(ev)
    return got_by_user

def sync_recharges():
    try:
        sync_recharges_real()
    except Exception as e:
        log.exception("Syncing recharges:")

def sync_recharges_real():
    data = requests.get(config.money_url,
        auth=HTTPBasicAuth(config.money_user, config.money_password))
    recharges = data.json()
    session = get_session()
    got_by_user = get_existing(session)

    for uid, charges in recharges.iteritems():
        log.info("Syncing recharges for user %s", uid)
        if uid not in got_by_user:
            log.info("First recharge for user %s!", uid)
            got_by_user[uid] = []
        got = got_by_user[uid]
        for charge in charges:
            charge_date = datetime.strptime(charge['date'], "%Y-%m-%d")
            charge_amount = Decimal(charge['amount'])
            log.debug("charge: %s, %s", charge, charge_date)
            found = False
            for exist in got:
                if exist.timestamp != charge_date: continue
                if exist.amount != charge_amount: continue
                # found a matching one
                found = True
                break
            if found: continue

            handle_transferred(charge, charge_amount, charge_date, got, session,
                uid)


def handle_transferred(charge, charge_amount, charge_date, got, session, uid):
    log.info("User %s transferred %s on %s: %s",
        uid, charge_amount, charge_date, charge)
    ev = RechargeEvent(uid, helper_user, charge_amount, charge_date)
    got.append(ev)
    session.add(ev)
    session.commit()
    try:
        user = Users.get_by_id(uid)
        if not user:
            log.error("could not find user %s to send email", uid)
        else:
            subject = "Aufladung EUR %s für %s" % (charge_amount, user['name'])
            text = "Deine Aufladung über %s € am %s mit Text '%s' war erfolgreich." % (
            charge_amount, charge_date, charge['info'])
            send_summary_now(3600 * 24 * 14, "2 Wochen",
                session, user, force=True, subject=subject,
                addltext=text)
    except:
        log.exception("sending notification mail:")


if __name__ == "__main__":
    sync_recharges()
