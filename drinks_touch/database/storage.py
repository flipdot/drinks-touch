from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

import config
from env import is_pi

engine = create_engine(config.POSTGRES_CONNECTION_STRING)
Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = Session.query_property()

if not is_pi():
    import logging

    logger = logging.getLogger("sqlalchemy.engine")
    logger.setLevel(getattr(logging, config.LOGLEVEL))


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import database.models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_session():
    # Session.remove()
    return Session
