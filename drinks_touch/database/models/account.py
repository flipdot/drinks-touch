import logging
from decimal import Decimal

from sqlalchemy import Column, Integer, String, UUID, DateTime, Boolean, func
from sqlalchemy.sql import text


from database.storage import Base, Session, with_db

logger = logging.getLogger(__name__)


class Account(Base):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True)
    ldap_id = Column(String(20), unique=True)
    ldap_path = Column(String(50), unique=True)
    keycloak_sub = Column(UUID, unique=True)
    enabled = Column(Boolean, default=True)

    name = Column(String(50), unique=True)
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
    tx_history_visible = Column(Boolean, default=False)

    @with_db
    def _get_legacy_balance(self):
        sql = text(
            """
            SELECT user_id, count(*) AS amount
            FROM scanevent
            WHERE user_id = :user_id
            GROUP BY user_id
            """
        )
        row = Session().execute(sql, {"user_id": self.ldap_id}).fetchone()
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
        row = Session().execute(sql, {"user_id": self.ldap_id}).fetchone()
        if not row:
            credit = 0
        else:
            credit = row.amount

        return credit - cost

    @with_db
    def _get_tx_balance(self):
        from database.models import Tx

        return Session().query(func.sum(Tx.amount)).filter(
            Tx.account_id == self.id,
        ).scalar() or Decimal(0)

    @property
    def balance(self):
        legacy_balance = self._get_legacy_balance()
        tx_balance = self._get_tx_balance()
        if legacy_balance != tx_balance:
            logger.error(
                f"Balance mismatch for account {self.id}: "
                f"Legacy balance: {legacy_balance}, Tx balance: {tx_balance}"
            )
        return tx_balance

    def get_recharges(self):
        from database.models import RechargeEvent

        return RechargeEvent.query.filter(
            RechargeEvent.user_id == self.ldap_id
        ).order_by(RechargeEvent.timestamp.desc())
