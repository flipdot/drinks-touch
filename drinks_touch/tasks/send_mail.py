from datetime import datetime
from time import sleep

from babel import dates
import config
from database.models import Account
from database.storage import Session
from notifications.notification import (
    render_jinja_template,
    send_notification,
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
                self._fail()
                return
            # send_summaries()
            if self.sig_killed:
                self._fail()
                return
            self.logger.info("Mail sending completed.")

    def send_low_balances(self):
        accounts = Session().query(Account).filter(Account.email.isnot(None)).all()
        for i, account in enumerate(accounts):
            self.progress = (i + 1) / len(accounts)
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
            return

        delta = datetime.now() - account.last_balance_warning_email_sent_at
        account_info = f"Account {account.id:3} {account.balance:7}€"
        if delta < config.REMIND_MAIL_DELTA_FOR_MINIMUM_BALANCE:
            self.logger.info(
                f"{account_info} | Skip, mailed {dates.format_timedelta(delta, locale='en_US')} ago"
            )
            sleep(0.5)
            return

        self.logger.info(f"{account_info} | Sending reminder")
        sleep(0.5)
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
