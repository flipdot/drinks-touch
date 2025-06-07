from datetime import datetime, timedelta

from babel import dates
import config
from database.models import Account
from database.storage import Session
from notifications.notification import (
    render_jinja_template,
    send_notification,
    get_drinks_consumed,
    get_recharges,
    format_drinks,
    format_recharges,
    FOOTER,
)
from tasks.base import BaseTask


class SendMailTask(BaseTask):
    LABEL = "Sende E-Mails"
    ON_STARTUP = True

    def run(self):
        with Session().begin():
            self.logger.info("Sending negative balance reminders...")
            self.send_low_balances()
            if self.sig_killed:
                raise Exception("Task was killed while sending low balances")
            self.logger.info("Sending summaries...")
            self.send_summaries()
            if self.sig_killed:
                raise Exception("Task was killed while sending summaries")
            self.logger.info("Mail sending completed.")

    def send_low_balances(self):
        accounts = Session().query(Account).filter(Account.email.isnot(None)).all()
        for i, account in enumerate(accounts):
            self.progress = (i + 1) / len(accounts) / 2
            if self.sig_killed:
                return
            self.send_low_balance(account)
            continue

    def send_low_balance(self, account: Account):
        assert account.email, "Account has no email"

        if account.balance >= config.MINIMUM_BALANCE:
            # reset time
            # TODO: It's a bit misleading when looking in the DB,
            #  because it will contain a timestamp at which the user didn't
            #  actually got an email.
            #  Maybe we can instead store the time at which the balance went negative
            account.last_balance_warning_email_sent_at = datetime.now()
            Session().flush()
            return

        delta = datetime.now() - account.last_balance_warning_email_sent_at
        account_info = f"Account {account.id:3} {account.balance:7}€"
        if delta < config.REMIND_MAIL_DELTA_FOR_MINIMUM_BALANCE:
            self.logger.info(
                f"{account_info} | Skip, mailed {dates.format_timedelta(delta, locale='en_US')} ago"
            )
            return

        self.logger.info(f"{account_info} | Sending reminder")
        context = {
            "delta": delta,
            "minimum_balance": config.MINIMUM_BALANCE,
            "balance": account.balance,
            "uid": account.ldap_id,
        }
        # TODO: the template tells the user that he "has a negative balance
        #  since {delta}", but as a delta we pass the time since the last email
        #  was sent. This is not the same as the time since the balance went
        #  negative. This should be fixed.
        content_html = render_jinja_template("low_balance.html", **context)
        content_text = render_jinja_template("low_balance.txt", **context)

        send_notification(
            account.email,
            "Negatives Guthaben",
            content_text,
            content_html,
            account.ldap_id,
        )

        account.last_balance_warning_email_sent_at = datetime.now()
        Session().flush()

    def send_summaries(self):
        accounts = Session().query(Account).filter(Account.email.isnot(None)).all()
        for i, account in enumerate(accounts):
            self.progress = 0.5 + (i + 1) / len(accounts) / 2
            if self.sig_killed:
                return
            self.send_summary(account, "Getränkeübersicht")

    def send_summary(self, account: Account, subject):
        assert account.email, "Account has no email"

        frequency_str = account.summary_email_notification_setting

        if last_noti := account.last_summary_email_sent_at:
            delta = datetime.now() - last_noti
        else:
            delta = timedelta.max

        if delta < config.MAIL_SUMMARY_DELTA.get(frequency_str, timedelta.max):
            return

        content_text = ""

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
        content_html = render_jinja_template(
            "main.html",
            with_report=True,
            balance=account.balance,
            last_drink_notification_sent_at=account.last_summary_email_sent_at,
            drinks=drinks_consumed,
            recharges=recharges,
            minimum_balance=config.MINIMUM_BALANCE,
            uid=account.ldap_id,
        )

        if len(drinks_consumed) == 0 and len(recharges) == 0:
            return

        self.logger.info(
            f"Account {account.id:3} | Summary mail, {len(drinks_consumed):2} drinks, {len(recharges):2} recharges"
        )
        send_notification(
            account.email,
            subject,
            content_text,
            content_html,
            account.ldap_id,
        )

        account.last_summary_email_sent_at = datetime.now()
        Session().flush()
