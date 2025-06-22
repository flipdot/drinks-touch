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


def with_db_session(func):
    """
    A decorator that injects an SQLAlchemy session into the decorated method.

    The session is managed as a unit of work: it's acquired, passed to the method,
    committed on success, rolled back on exception, and always closed/removed.

    The decorated method must accept 'session: Session' as one of its parameters.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if "session" in kwargs:
            # If a session is explicitly passed, use it directly.
            # This allows for nested calls
            return func(*args, **kwargs)

        # Otherwise, acquire a new session using the context manager
        # for this unit of work.
        with Session() as session:
            # Inject the session into the function's keyword arguments
            kwargs["session"] = session
            return func(*args, **kwargs)

    return wrapper
