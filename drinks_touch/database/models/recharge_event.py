import datetime

from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey

from database.storage import Base


class RechargeEvent(Base):
    __tablename__ = "rechargeevent"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(20), unique=False)
    helper_user_id = Column(String(20), unique=False)
    amount = Column(Numeric, unique=False)
    timestamp = Column(DateTime(), unique=False)
    # foreign key to transaction, purpose is to track migration progress
    tx_id = Column(ForeignKey("tx.id"), nullable=True)

    def __init__(
        self,
        user_id,
        helper_user_id,
        amount,
        timestamp=datetime.datetime.now(),
        tx_id=None,
    ):
        # self.user_id = bytes.decode(user_id)
        self.user_id = user_id
        self.helper_user_id = helper_user_id
        self.amount = amount
        self.timestamp = timestamp
        self.tx_id = tx_id
