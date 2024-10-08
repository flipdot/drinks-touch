import math
from datetime import datetime

from sqlalchemy import Column, Integer, String, UUID, DateTime

from database.storage import Base, get_session
from users.users import Users


class Account(Base):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True)
    ldap_id = Column(String(20), unique=True)
    ldap_path = Column(String(50), unique=True)
    keycloak_sub = Column(UUID, unique=True)

    name = Column(String(50), unique=False)
    id_card = Column(String(50), unique=True)
    last_email_sent_at = Column(DateTime(), unique=False)
    last_drink_notification_sent_at = Column(DateTime(), unique=False)

    @classmethod
    def sync_all_from_ldap(cls):
        session = get_session()

        ldap_users = Users.get_all(include_temp=True)

        # sort by id, but put None last
        # this way, our oldest flipdot members get the smallest ids.
        # Not really necessary, but it's nice to keep history.
        ldap_users = sorted(ldap_users, key=lambda x: x["id"] or math.inf)
        for user in ldap_users:
            if user["id"] == 10000 and user["name"] == "malled2":
                # malled how did you manage to get two accounts with the same id?
                continue

            # find existing account based on ldap_path (the anonymous accounts don't have an ldap_id)
            account = (
                session.query(Account).filter(Account.ldap_path == user["path"]).first()
            )
            if not account:
                account = Account(
                    ldap_id=user["id"],
                    ldap_path=user["path"],
                )

            account.name = user["name"]
            account.id_card = user["id_card"]
            if ts := user["lastEmailed"]:
                account.last_email_sent_at = datetime.fromtimestamp(ts)
            if ts := user["lastDrinkNotification"]:
                account.last_drink_notification_sent_at = datetime.fromtimestamp(ts)

            session.add(account)

        session.commit()
