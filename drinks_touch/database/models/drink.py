from sqlalchemy import Column, Integer, String, DateTime, Numeric

from database.storage import Base


class Drink(Base):
    __tablename__ = "drink"
    id = Column(Integer, primary_key=True)
    ean = Column(String(20), unique=False)  # TODO: Should be unique
    name = Column(String(40), unique=False)
    size = Column(Numeric, unique=False)
    timestamp = Column(DateTime(), unique=False)
    price = Column(Numeric(precision=8, scale=2, asdecimal=True))
