import math
from datetime import datetime

from sqlalchemy import Column, Integer, String, UUID, DateTime
from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql import text

from database.storage import Base, Session
from users.users import Users


class Account(Base):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True)
    ldap_id = Column(String(20), unique=True)
    ldap_path = Column(String(50), unique=True)
    keycloak_sub = Column(UUID, unique=True)

    name = Column(String(50), unique=False)
    id_card = Column(String(50), unique=True)
    # > In addition to restrictions on syntax, there is a length limit on
    # > email addresses.  That limit is a maximum of 64 characters (octets)
    # > in the "local part" (before the "@") and a maximum of 255 characters
    # > (octets) in the domain part (after the "@") for a total length of 320
    # > characters.  Systems that handle email should be prepared to process
    # > addresses which are that long, even though they are rarely
    # > encountered.
    # https://datatracker.ietf.org/doc/html/rfc3696.html#section-3
    email = Column(String(320), unique=True)
    last_balance_warning_email_sent_at = Column(DateTime(), unique=False)
    last_summary_email_sent_at = Column(DateTime(), unique=False)
    summary_email_notification_setting = Column(String(50), unique=False)

    @staticmethod
    def sync_all_from_ldap(progress=None):
        if progress is None:
            progress = lambda *args, **kwargs: None  # noqa: E731

        ldap_users = Users.get_all(include_temp=True)

        # sort by id, but put None last
        # this way, our oldest flipdot members get the smallest ids.
        # Not really necessary, but it's nice to keep history.
        ldap_users = sorted(ldap_users, key=lambda x: x["id"] or math.inf)
        for i, user in enumerate(ldap_users):
            progress(i / len(ldap_users))
            if user["id"] == 10000 and user["name"] == "malled2":
                # malled how did you manage to get two accounts with the same id?
                continue

            # find existing account based on ldap_path (the anonymous accounts don't have an ldap_id)
            try:
                account = (
                    Session()
                    .query(Account)
                    .filter(Account.ldap_path == user["path"])
                    .one()
                )
            except NoResultFound:
                account = Account(
                    ldap_id=user["id"],
                    ldap_path=user["path"],
                )

            account.name = user["name"]
            account.id_card = user["id_card"]
            account.email = user["email"]
            account.summary_email_notification_setting = user["drinksNotification"]

            # Only update the last email sent at if it is not set yet
            # This way we can start writing the new value to the DB without needing
            # to worry about it getting overridden on sync.
            if not account.last_balance_warning_email_sent_at and (
                ts := user["lastEmailed"]
            ):
                account.last_balance_warning_email_sent_at = datetime.fromtimestamp(ts)
            if not account.last_summary_email_sent_at and (
                ts := user["lastDrinkNotification"]
            ):
                account.last_summary_email_sent_at = datetime.fromtimestamp(ts)

            Session().add(account)

    @property
    def balance(self):
        sql = text(
            """
                SELECT user_id, count(*) AS amount
                FROM scanevent
                WHERE user_id = :user_id
                GROUP BY user_id
            """
        )
        row = Session().connection().execute(sql, {"user_id": self.ldap_id}).fetchone()
        if not row:
            cost = 0
        else:
            cost = row.amount

        sql = text(
            """
                SELECT user_id, sum(amount) AS amount
                FROM rechargeevent
                WHERE user_id = :user_id
                GROUP BY user_id
            """
        )
        row = Session().connection().execute(sql, {"user_id": self.ldap_id}).fetchone()
        if not row:
            credit = 0
        else:
            credit = row.amount

        return credit - cost
