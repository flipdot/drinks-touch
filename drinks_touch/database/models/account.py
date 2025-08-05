import logging
from decimal import Decimal

from sqlalchemy import Column, Integer, String, UUID, DateTime, Boolean, func


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

    @property
    @with_db
    def balance(self):
        from database.models import Tx

        return Session().query(func.sum(Tx.amount)).filter(
            Tx.account_id == self.id,
        ).scalar() or Decimal(0)

    def get_recharges(self):
        from database.models import RechargeEvent

        return RechargeEvent.query.filter(
            RechargeEvent.user_id == self.ldap_id
        ).order_by(RechargeEvent.timestamp.desc())
