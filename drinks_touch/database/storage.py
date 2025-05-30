from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

import config
from env import is_pi

engine = create_engine(config.POSTGRES_CONNECTION_STRING)
Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base(
    metadata=MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )
)
Base.query = Session.query_property()

if not is_pi():
    import logging

    logger = logging.getLogger("sqlalchemy.engine")
    logger.setLevel(getattr(logging, config.LOGLEVEL))


def get_session():
    # Session.remove()
    return Session
