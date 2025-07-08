from sqlalchemy import Column, Text, Date, Integer
from sqlalchemy.sql import func

from database.storage import Base


class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True)
    date = Column(Date(), nullable=False, server_default=func.current_date())
    ean = Column(Text(), nullable=False)
