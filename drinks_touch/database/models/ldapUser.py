from sqlalchemy import Column, Integer, String, Boolean

from database.storage import Base


class LdapUser(Base):
    __tablename__ = "ldapUsers"
    id = Column(Integer, primary_key=True)
    ldapId = Column(String(20), unique=False)
    name = Column(String(50), unique=False)
    path = Column(String(50), unique=False)
    id_card = Column(String(50), unique=False)
    is_card = Column(Boolean(), unique=False)

    def __init__(self, ldap_id, name, path, id_card, is_card):
        self.ldapId = ldap_id
        self.name = name
        self.path = path
        self.id_card = id_card
        self.is_card = is_card
