import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database.storage import Base

class ScanEvent(Base):
    __tablename__ = 'scanevent'
    id = Column(Integer, primary_key=True)
    barcode = Column(String(20), unique=False)
    user_id = Column(String(20), unique=False)
    timestamp = Column(DateTime(), unique=False)
    uploaded_to_influx = Column(Boolean(), unique=False)

    def __init__(self, barcode=None, user_id="1", timestamp=datetime.datetime.now()):
        self.barcode = barcode
        self.timestamp = timestamp
        self.user_id = user_id

    def __repr__(self):
        return '<Barcode %r, User %r>' % (self.barcode, self.user_id)