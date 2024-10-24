import os
from datetime import timedelta
from pathlib import Path

import dotenv

dotenv.load_dotenv()

MONEY_URL = os.environ.get("MONEY_URL", "https://somewhere/x.json")
MONEY_USER = os.environ.get("MONEY_USER", "my_user")
MONEY_PASSWORD = os.environ.get("MONEY_PASSWORD", "my_basicauth_passwd")

LDAP_HOST = os.environ.get("LDAP_HOST", "ldap://127.0.0.1")
LDAP_USER = os.environ.get("LDAP_USER", "cn=admin,dc=flipdot,dc=org")
LDAP_PW = os.environ.get("LDAP_PW", "admin")

DEBUG_UI_ELEMENTS = os.environ.get("DEBUG_UI_ELEMENTS", "False") in [
    "True",
    "true",
    "1",
    "yes",
]

COLORS = {
    "infragelb": (246, 198, 0),
    "disabled": (50, 50, 50),
}

if bn := os.environ.get("BUILD_NUMBER"):
    BUILD_NUMBER = bn
else:
    BUILD_NUMBER = (
        os.popen("git describe --tags --dirty").read().strip() or "git is not available"
    )

GIT_REPO_AVAILABLE = (
    os.popen("git rev-parse --is-inside-work-tree").read().strip() == "true"
)
REPO_PATH = Path(__file__).parent

OIDC_DISCOVERY_URL = os.environ.get(
    "OIDC_DISCOVERY_URL",
    "http://localhost:8080/realms/flipdot/.well-known/openid-configuration",
)
OIDC_CLIENT_ID = os.environ.get("OIDC_CLIENT_ID", "drinks-touch")
# Client secret default from the shipped realm.json
OIDC_CLIENT_SECRET = os.environ.get(
    "OIDC_CLIENT_SECRET", "ozlsD9WZi8PfsnYwPO3UFoIUBjPyS4Bd"
)

# Refresh the token X seconds before it expires
OIDC_REFRESH_BUFFER = 10

SENTRY_DSN = os.environ.get("SENTRY_DSN", "")

POSTGRES_CONNECTION_STRING = os.environ.get(
    "POSTGRES_CONNECTION_STRING", "postgresql://drinks:drinks@localhost/drinks"
)

MAIL_FROM = os.environ.get("MAIL_FROM", "flipdot-noti@mailpit")
MAIL_PW = os.environ.get("MAIL_PW", "pw")
MAIL_HOST = os.environ.get("MAIL_HOST", "localhost")
MAIL_PORT = os.environ.get("MAIL_PORT", 1025)
MAIL_USE_STARTTLS = os.environ.get("MAIL_USE_STARTTLS", "False") in [
    "True",
    "true",
    "1",
]

MINIMUM_BALANCE = -5
REMIND_MAIL_DELTA_FOR_MINIMUM_BALANCE = timedelta(weeks=1)
MAIL_SUMMARY_DELTA = {
    "daily": timedelta(days=1),
    "instant and daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
    "instant and weekly": timedelta(weeks=1),
}

SCANNER_DEVICE_PATH = os.environ.get("SCANNER_DEVICE_PATH", "/dev/ttyACM0")

WEBSERVER_PORT = os.environ.get("WEBSERVER_PORT", 5002)

FPS = 30

FONTS = {"monospace": "DejaVu Sans Mono", "sans serif": "DejaVu Sans"}

LOGLEVEL = os.environ.get("LOGLEVEL", "WARNING")

# DEVELOPMENT VARIABLES #

# Send any mail to the user with the given id.
# Evaluates to MAIL_FROM by default.
FORCE_MAIL_TO_UID = os.environ.get("FORCE_MAIL_TO_UID", None)

FULLSCREEN = os.environ.get("FULLSCREEN", "True") in ["True", "true", "1", "yes"]
