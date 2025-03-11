from sqlalchemy import String, Column

from database.storage import Base


class AppSettings(Base):
    __tablename__ = "appsettings"
    key = Column(String(50), primary_key=True)
    value = Column(String(200), unique=False)
