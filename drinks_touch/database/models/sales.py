import uuid

from sqlalchemy import Column, UUID, Text, Date
from sqlalchemy.sql import func

from database.storage import Base


class Sales(Base):
    __tablename__ = "sales"
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    date = Column(Date(), nullable=False, server_default=func.current_date())
    ean = Column(Text(), nullable=False)
