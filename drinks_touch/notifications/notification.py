import functools
import time
from datetime import datetime, timedelta

import babel.dates
import jinja2
import logging
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from premailer import transform
from sqlalchemy import text, select

import config
from database.models.account import Account
from database.models.recharge_event import RechargeEvent
from database.storage import Session

logger = logging.getLogger(__name__)

SUBJECT_PREFIX = "[fd-noti]"

FOOTER = """
Besuchen Sie uns bald wieder!

Einstellungen: https://ldap.flipdot.space/
Aufladen: https://drinks.flipdot.space
Oder per SEPA:
  Kontoinhaber: flipdot e.V.
  IBAN: DE07 5205 0353 0001 1477 13
  Verwendungszweck: "drinks {uid} hinweistext"
  Der Hinweistext ist frei wählbar.
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


def send_drink(account: Account, drink, with_summary=False):
    try:
        if account.email and "instant" in account.summary_email_notification_setting:
            content_text = (
                "Du hast das folgende Getränk getrunken: {drink_name}.".format(
                    drink_name=drink["name"]
                )
            )
            content_html = render_jinja_html("instant.html", drink_name=drink["name"])

            if not with_summary:
                content_text += FOOTER.format(uid=account.ldap_id)
                content_html = render_jinja_html("main.html", prepend_html=content_html)
                send_notification(
                    account,
                    "Getränk getrunken",
                    content_text,
                    content_html,
                    account.ldap_id,
                )
                return

            send_summary(
                account,
                subject="Getränk getrunken",
                prepend_text=content_text,
                prepend_html=content_html,
                force=True,
            )
    except Exception:
        logger.exception("while sending drink noti")


def send_low_balances(with_summary=True):
    with Session() as session:
        if config.FORCE_MAIL_TO_UID:
            account = (
                session.query(Account)
                .filter(Account.ldap_id == config.FORCE_MAIL_TO_UID)
                .first()
            )
            send_low_balance(
                account,
                with_summary,
                force=True,
            )
            return

        query = select(Account).where(Account.email.isnot(None))
        accounts = session.scalars(query).all()
        for account in accounts:
            try:
                send_low_balance(account, with_summary)
            except Exception:
                logger.exception("while sending lowbalances:")
                continue
        session.commit()


def send_low_balance(account: Account, with_summary=False, force=False):
    assert account.email, "Account has no email"

    if not force and account.balance >= config.MINIMUM_BALANCE:
        # reset time
        # TODO: It's a bit misleading when looking in the DB,
        #  because it will contain a timestamp at which the user didn't
        #  actually got an email.
        #  Maybe we can instead store the time at which the balance went negative
        account.last_balance_warning_email_sent_at = datetime.now()
        return

    delta = datetime.now() - account.last_balance_warning_email_sent_at
    if delta < config.REMIND_MAIL_DELTA_FOR_MINIMUM_BALANCE:
        return

    logger.info(
        "%s's low balance last emailed %s ago. Mailing now.",
        account.name,
        babel.dates.format_timedelta(delta, locale="en_US"),
    )
    content_text = (
        "Du hast seit mehr als {diff_days} "
        "ein Guthaben von unter {minimum_balance}€!\n"
        "Aktueller Kontostand: {balance:.2f}€.\n"
        "Zum Aufladen im Space-Netz https://drinks.flipdot.space/ besuchen."
    ).format(
        diff_days=babel.dates.format_timedelta(delta, locale="de_DE"),
        minimum_balance=config.MINIMUM_BALANCE,
        balance=account.balance,
    )
    content_html = render_jinja_html(
        "low_balance.html",
        # TODO: the template tells the user that he "has a negative balance
        #  since {delta}", but as a delta we pass the time since the last email
        #  was sent. This is not the same as the time since the balance went
        #  negative. This should be fixed.
        delta=delta,
        minimum_balance=config.MINIMUM_BALANCE,
        balance=account.balance,
        uid=account.ldap_id,
    )

    if not with_summary:
        content_text += FOOTER.format(uid=account.ldap_id)
        content_html = render_jinja_html(
            "main.html",
            prepend_html=content_html,
            uid=account.ldap_id,
        )

        send_notification(
            account.email,
            "Negatives Guthaben",
            content_text,
            content_html,
            account.ldap_id,
        )
        return

    send_summary(
        account,
        subject="Negatives Guthaben",
        prepend_text=content_text,
        prepend_html=content_html,
        force=True,
    )

    account.last_balance_warning_email_sent_at = datetime.now()


def send_summaries():
    with Session() as session:
        if config.FORCE_MAIL_TO_UID:
            query = select(Account).filter(Account.ldap_id == config.FORCE_MAIL_TO_UID)
            account = session.scalars(query).one()
            send_summary(
                account,
                "Getränkeübersicht",
                force=True,
            )
            return

        query = select(Account).filter(Account.email.isnot(None))
        accounts = session.scalars(query).all()

        for account in accounts:
            try:
                send_summary(account, "Getränkeübersicht")
            except Exception:
                logger.exception("Error while sending summary for %s", account.name)
                continue
        session.commit()


def send_summary(
    account: Account, subject, prepend_text=None, prepend_html=None, force=False
):
    assert account.email, "Account has no email"

    frequency_str = account.summary_email_notification_setting

    if last_noti := account.last_summary_email_sent_at:
        delta = datetime.now() - last_noti
    else:
        delta = timedelta.max

    if not force and delta < config.MAIL_SUMMARY_DELTA.get(
        frequency_str, timedelta.max
    ):
        return

    logger.info(
        "%s's summary last emailed %s ago. Mailing now.",
        account.name,
        babel.dates.format_timedelta(delta, locale="en_US"),
    )

    content_text = ""

    if prepend_text:
        content_text += prepend_text + "\n==========\n"

    content_text += (
        "Hier ist deine Getränkeübersicht seit {since}.\n"
        "Dein aktuelles Guthaben beträgt EUR {balance:.2f}.\n".format(
            since=account.last_summary_email_sent_at, balance=account.balance
        )
    )

    drinks_consumed = get_drinks_consumed(account)
    recharges = get_recharges(account)

    if drinks_consumed:
        content_text += format_drinks(drinks_consumed)

    if recharges:
        content_text += format_recharges(recharges)

    content_text += FOOTER.format(uid=account.ldap_id)
    content_html = render_jinja_html(
        "main.html",
        with_report=True,
        balance=account.balance,
        last_drink_notification_sent_at=account.last_summary_email_sent_at,
        drinks=drinks_consumed,
        recharges=recharges,
        prepend_html=prepend_html,
        minimum_balance=config.MINIMUM_BALANCE,
        uid=account.ldap_id,
    )

    if len(drinks_consumed) == 0 and len(recharges) == 0 and not force:
        logger.info("Nothing to mail to %s", account.email)
        return

    logger.info(
        "Got %d drinks and %d recharges. Mailing.", len(drinks_consumed), len(recharges)
    )
    send_notification(
        account.email,
        subject,
        content_text,
        content_html,
        account.ldap_id,
    )

    account.last_summary_email_sent_at = datetime.now()


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
        Session()
        .connection()
        .execute(sql, {"userid": account.ldap_id})
        .mappings()
        .all()
    )
    return drinks_consumed


def get_recharges(account: Account) -> list[RechargeEvent]:
    query = (
        Session().query(RechargeEvent).filter(RechargeEvent.user_id == account.ldap_id)
    )
    if account.last_summary_email_sent_at:
        query = query.filter(
            RechargeEvent.timestamp >= account.last_summary_email_sent_at
        )
    return query.order_by(RechargeEvent.timestamp).all()


def render_jinja_html(
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
