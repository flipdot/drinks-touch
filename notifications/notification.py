# -*- coding:utf-8 -*-
import logging
import smtplib
import threading
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

from sqlalchemy import text

from database.models.recharge_event import RechargeEvent
from database.storage import get_session
from env import is_pi
from users.users import Users

SUBJECT_PREFIX = "[fd-noti] "
MAIL_FROM = "flipdot-noti@vega.uberspace.de"

# lower and we send mails every x days!
minimum_balance = -5
remind_mail_every_x_hours = 24 * 7

FOOTER = """\n
Besuchen Sie uns bald wieder!
Einstellungen: http://ldap.fd/
Aufladen: http://drinks-touch.fd/
"""

with open('mail_pw', 'r') as pw:
    mail_pw = pw.read().replace('\n', '')

def send_notification_newthread(to_address, subject, message):
    send_thread = threading.Thread(
        target=send_notification,
        args=(to_address, subject, message)
    )
    send_thread.daemon = True
    send_thread.start()

def send_notification(to_address, subject, message):
    msg = MIMEText(message,_charset='utf-8')

    msg['Subject'] = subject
    msg['From'] = MAIL_FROM
    msg['To'] = to_address
    msg['Date'] = formatdate(time.time(), localtime=True)
    msg['Message-id'] = make_msgid()

    logging.info("Mailing %s: '%s'", to_address, subject)
    logging.debug("Content: %s", message)
    s = smtplib.SMTP()
    s.connect(host='vega.uberspace.de', port=587)
    s.ehlo()
    s.starttls()
    s.login(user=MAIL_FROM, password=mail_pw)
    s.sendmail(MAIL_FROM, [to_address], msg.as_string())
    s.quit()

def send_drink(user, drink, balance):
    try:
        user_email = user['email']

        if user_email and user['meta']['drink_notification'] == 'instant':
            mail_msg = ("Du hast das folgende Getränk getrunken {drink_name}" \
                       "\n\nVerbleibendes Guthaben: EUR {balance}"+ \
                       FOOTER).format(
                drink_name=drink['name'], balance=balance)
            send_notification_newthread(user_email,
                SUBJECT_PREFIX + "Getränk getrunken", mail_msg)
    except Exception as e:
        logging.error(e)
        pass

def send_lowbalances():
    if not is_pi():
        return
    session = get_session()
    for user in Users.get_all():
        try:
            send_lowbalance(session, user)
        except Exception as e:
            logging.exception("while sending lowbalances:")
            continue

def send_lowbalance(session, user):
    now = time.time()

    balance = Users.get_balance(user['id'])
    if balance >= minimum_balance:
        # set time to okay
        user["last_emailed"] = time.time()
        Users.save(user)
        return
    diff = now - user['last_emailed']
    last_emailed_hours = diff / 60 / 60
    last_emailed_days = last_emailed_hours / 24
    if last_emailed_hours > remind_mail_every_x_hours:
        print user['name'], "balance last emailed", last_emailed_days, "days (", \
            last_emailed_hours, "hours) ago. Mailing now."

        text = ("Du hast seit mehr als {limit_days} Stunden ein "
            "Guthaben unter EUR {limit}!\n\n"
            "Dein Guthaben betraegt: EUR {balance}\n\n"
            "Zum aufladen geh (im Space-Netz) auf http://drinks-touch.fd/" +
            FOOTER
        ).format(
            limit_days=remind_mail_every_x_hours / 24,
            limit=minimum_balance, balance=balance)
        send_summary_now(14*24*3600, "2 Wochen", session, user,
            subject="Negatives Guthaben",
            force=True, addltext=text)
        user["last_emailed"] = time.time()
        Users.save(user)

def send_summaries():
    session = get_session()
    if not is_pi():
        #u = Users.get_all('cfstras')[0]
        #send_summary(session, u, u['email'])
        return
    for user in Users.get_all():
        try:
            send_summary(session, user)
        except Exception as e:
            logging.exception("While sending summary for %s", user)
            continue

frequencies = {
    "daily": 60 * 60 * 24,
    "weekly": 60 * 60 * 24 * 7,
}

def send_summary(session, user):
    now = time.time()
    frequency_str = user['meta']['drink_notification']
    if frequency_str not in frequencies.keys():
        return
    freq_secs = frequencies[frequency_str]
    last_emailed = user['meta']['last_drink_notification']
    last_emailed_str = datetime.fromtimestamp(last_emailed).isoformat()
    diff = now - last_emailed
    last_emailed_hours = diff / 60 / 60
    last_emailed_days = last_emailed_hours / 24
    if diff > freq_secs:
        print user['name'], "summary last emailed", last_emailed_days, "days (", \
            last_emailed_hours, "hours) ago. Mailing now."
        send_summary_now(freq_secs, last_emailed_str, session, user)

 
def send_summary_now(since_secs, since_text, session, user, subject=None, force=False, addltext=""):
    mail_msg, num_recharges, num_drinks = format_mail(session, user,
        since_secs, since_text, addltext)
    email = user['email']
    if not email:
        print "User %s has no email. skipping." % user['name']

    if not subject:
        subject = "Getränkeübersicht für %s" % user['name']
    if num_drinks == 0 and num_recharges == 0 and not force:
        print "got no rows. skipping."
        return

    print "got %d drinks and %d recharges. mailing." % (num_drinks, num_recharges)
    send_notification(email, SUBJECT_PREFIX + subject, mail_msg)
    user['meta']["last_drink_notification"] = time.time()
    Users.save(user)


def format_mail(session, user, since_secs, since_text, addltext=""):
    mail_msg = "Hier ist deine Getränkeübersicht seit {since}:\n" \
               "Dein aktuelles Guthaben beträgt EUR {balance}.\n" \
        .format(since=since_text, balance=Users.get_balance(user['id']))
    drinks_consumed = get_drinks_consumed(session, user, since_secs)
    recharges = get_recharges(session, user)
    if addltext:
        mail_msg += str(addltext) + "\n"
    mail_msg += format_drinks(drinks_consumed)
    mail_msg += format_recharges(recharges)
    mail_msg += FOOTER
    return mail_msg, len(recharges), len(drinks_consumed)


def format_recharges(recharges):
    recharges_fmt = "\n\nAufladungen in den letzten 4 Wochen:\n" \
                    "datum                mit             aufgeladen\n"
    for event in recharges:
        date = event.timestamp.strftime("%F %T Z")
        mit = event.helper_user_id
        try:
            mit = Users.get_by_id(mit)['name']
        except:
            pass
        amount = event.amount
        recharges_fmt += "% 20s %15s %s" % (date, mit, amount)
    return recharges_fmt


def format_drinks(drinks_consumed):
    drinks_fmt = "    #      datum                     drink  groesse\n"
    for i, event in enumerate(drinks_consumed):
        date = event['timestamp'].strftime("%F %T Z")
        name = event['name']
        size = event['size']
        drinks_fmt += u"  % 3d % 20s % 15s % 5s l\n" % (
            i, date, name, size if size else "?"
        )
    return drinks_fmt


def get_recharges(session, user):
    recharges = session.query(RechargeEvent) \
        .filter(RechargeEvent.user_id == user['id']) \
        .filter(RechargeEvent.timestamp >= datetime.utcnow() - timedelta(weeks=4)) \
        .order_by(RechargeEvent.timestamp) \
        .all()
    return recharges


def get_drinks_consumed(session, user, since_secs):
    sql = text("""SELECT
    se.barcode,
    se.timestamp,
    d.name,
    d.size
FROM scanevent se
    LEFT OUTER JOIN drink d ON d.ean = se.barcode
WHERE user_id = :userid
    AND se.timestamp > NOW() - INTERVAL '%d seconds'
ORDER BY se.timestamp
        """ % (since_secs))
    drinks_consumed = session.connection().execute(sql,
        userid=user['id']).fetchall()
    return drinks_consumed
