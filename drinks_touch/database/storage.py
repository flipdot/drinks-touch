from functools import wraps

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

import config
from env import is_pi

engine = create_engine(
    config.POSTGRES_CONNECTION_STRING,
    connect_args={
        "application_name": "drinks_touch",
    },
)
Session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine, autobegin=False)
)
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
    logger.setLevel(logging.INFO)


def with_db(func):
    """
    A decorator that starts a transaction in the global SQLAlchemy session
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        session = Session()
        if session.in_transaction():
            with session.begin_nested():
                return func(*args, **kwargs)

        with session.begin():
            return func(*args, **kwargs)

    return wrapper
