from flask_oidc import OpenIDConnect
from flask_sqlalchemy import SQLAlchemy

from database.storage import Base

db = SQLAlchemy(
    model_class=Base,
    engine_options={
        "connect_args": {"application_name": "drinks_web"},
    },
)

oidc = OpenIDConnect()
