from sqlalchemy import String, Column

from database.storage import Base


class Metadata(Base):
    __tablename__ = "metadata"
    key = Column(String(50), primary_key=True)
    value = Column(String(200), unique=False)
