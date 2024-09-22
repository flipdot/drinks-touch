import os

MONEY_URL = os.environ.get("MONEY_URL", "https://somewhere/x.json")
MONEY_USER = os.environ.get("MONEY_USER", "my_user")
MONEY_PASSWORD = os.environ.get("MONEY_PASSWORD", "my_basicauth_passwd")

LDAP_HOST = os.environ.get("LDAP_HOST", "ldap://127.0.0.1")
LDAP_USER = os.environ.get("LDAP_USER", "cn=admin,dc=flipdot,dc=org")
LDAP_PW = os.environ.get("LDAP_PW", "admin")


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

SCANNER_DEVICE_PATH = os.environ.get("SCANNER_DEVICE_PATH", "/dev/ttyACM0")

WEBSERVER_PORT = os.environ.get("WEBSERVER_PORT", 5002)

FPS = 30

LOGLEVEL = os.environ.get("LOGLEVEL", "DEBUG")

# DEVELOPMENT VARIABLES #

# Send any mail to the user with the given id.
# Evaluates to MAIL_FROM by default.
FORCE_MAIL_TO_UID = os.environ.get("FORCE_MAIL_TO_UID", None)

# Do not fetch users from ldap.
# Use debug users instead.
USE_DEBUG_USERS = True

# ldap: do not save changes to users.
NO_USER_CHANGES = True
