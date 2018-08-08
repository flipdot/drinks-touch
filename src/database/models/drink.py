import datetime

from sqlalchemy import Column, Integer, String, DateTime, Numeric
from database.storage import Base

class Drink(Base):
    __tablename__ = 'drink'
    id = Column(Integer, primary_key=True)
    ean = Column(String(20), unique=False)
    name = Column(String(40), unique=False)
    size = Column(Numeric, unique=False)
    timestamp = Column(DateTime(), unique=False)

    def __init__(self, ean, name, size, timestamp=datetime.datetime.now()):
        self.ean = ean
        self.name = name
        self.size = size
        self.timestamp = timestamp
