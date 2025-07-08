import functools
import time
from datetime import datetime

import babel.dates
import jinja2
import logging
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from premailer import transform
from sqlalchemy import text

import config
from database.models.account import Account
from database.models.recharge_event import RechargeEvent
from database.storage import Session, with_db

logger = logging.getLogger(__name__)

SUBJECT_PREFIX = "[fd-noti]"

FOOTER = """
Besuche uns bald wieder!

Konto: https://login.flipdot.org/
Aufladen: https://drinks.flipdot.space
Oder per SEPA:
  Kontoinhaber: flipdot e.V.
  IBAN: DE07 5205 0353 0001 1477 13
  Verwendungszweck: drinks {uid} Freitext
"""


def send_notification(to_address, subject, content_text, content_html, uid):
    msg = MIMEMultipart("alternative")

    plain = MIMEText(content_text, "plain", _charset="utf-8")
    html = MIMEText(transform(content_html), "html", _charset="utf-8")

    msg.attach(plain)
    msg.attach(html)

    msg["Subject"] = Header(SUBJECT_PREFIX + " " + subject, "utf-8")
    msg["From"] = config.MAIL_FROM
    msg["To"] = to_address
    msg["Date"] = formatdate(time.time(), localtime=True)
    msg["Message-id"] = make_msgid()
    msg["X-LDAP-ID"] = str(uid)

    logger.info("Mailing %s: '%s'", to_address, subject)
    logger.debug("Content: ---\n%s\n---", content_text)

    s = smtplib.SMTP(config.MAIL_HOST, port=config.MAIL_PORT)
    s.connect(host=config.MAIL_HOST, port=config.MAIL_PORT)
    s.ehlo()
    if config.MAIL_USE_STARTTLS:
        s.starttls()
    s.login(user=config.MAIL_FROM, password=config.MAIL_PW)
    s.sendmail(config.MAIL_FROM, [to_address], msg.as_string())
    s.quit()


def send_drink(account: Account, drink):
    if not account.email or "instant" not in account.summary_email_notification_setting:
        return
    context = {
        "drink_name": drink["name"],
        "uid": account.ldap_id,
        "balance": account.balance,
    }
    content_text = render_jinja_template("instant.txt", **context)
    content_html = render_jinja_template("instant.html", **context)

    send_notification(
        account.email,
        "Getränk getrunken",
        content_text,
        content_html,
        account.ldap_id,
    )


def format_drinks(drinks_consumed):
    drinks_fmt = "\nGetrunken:\n"
    drinks_fmt += "    #                 datum                drink groesse\n"

    for i, event in enumerate(drinks_consumed):
        date = event["timestamp"].strftime("%F %T Z")
        name = event["name"]
        size = event["size"]
        drinks_fmt += "  % 3d % 15s % 20s % 5s l\n" % (
            i,
            date,
            name,
            size if size else "?",
        )

    return drinks_fmt


def format_recharges(recharges: list[RechargeEvent]):
    recharges_fmt = "\nAufladungen:\n" "    #                 datum     aufgeladen\n"

    for i, event in enumerate(recharges):
        date = event.timestamp.strftime("%F %T Z")
        amount = event.amount
        recharges_fmt += "  % 3d % 15s %10s\n" % (i, date, amount)

    return recharges_fmt


@with_db
def get_drinks_consumed(account: Account):
    if account.last_summary_email_sent_at:
        since_timestamp = account.last_summary_email_sent_at.timestamp()
    else:
        since_timestamp = 0
    sql = text(
        """SELECT
    se.barcode,
    se.timestamp,
    d.name,
    d.size
FROM scanevent se
    LEFT OUTER JOIN drink d ON d.ean = se.barcode
WHERE user_id = :userid
    AND se.timestamp >= TO_TIMESTAMP('%d')
ORDER BY se.timestamp"""
        % since_timestamp
    )
    drinks_consumed = (
        Session().execute(sql, {"userid": account.ldap_id}).mappings().all()
    )
    return drinks_consumed


@with_db
def get_recharges(account: Account) -> list[RechargeEvent]:
    query = (
        Session().query(RechargeEvent).filter(RechargeEvent.user_id == account.ldap_id)
    )
    if account.last_summary_email_sent_at:
        query = query.filter(
            RechargeEvent.timestamp >= account.last_summary_email_sent_at
        )
    return query.order_by(RechargeEvent.timestamp).all()


def render_jinja_template(
    file_name, template_loc="drinks_touch/notifications/templates", **context
):
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_loc))
    environment.filters["format_datetime"] = functools.partial(
        datetime.strftime, format="%d.%m.%Y %H:%M:%S"
    )
    environment.filters["format_date"] = functools.partial(
        datetime.strftime, format="%d.%m.%Y"
    )
    environment.filters["format_timedelta"] = functools.partial(
        babel.dates.format_timedelta, locale="de_DE"
    )
    return environment.get_template(file_name).render(context)
