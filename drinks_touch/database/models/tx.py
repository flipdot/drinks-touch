import uuid

from sqlalchemy import Column, UUID, Text, ForeignKey, Numeric, DateTime
from sqlalchemy.sql import func

from database.storage import Base


class Tx(Base):
    __tablename__ = "tx"
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    payment_reference = Column(Text(), nullable=True)
    ean = Column(Text(), nullable=True)
    account_id = Column(ForeignKey("account.id"), nullable=False)
    amount = Column(Numeric(precision=8, scale=2, asdecimal=True), nullable=False)
