import os

MONEY_URL = os.environ.get("MONEY_URL", "https://somewhere/x.json")
MONEY_USER = os.environ.get("MONEY_USER", "my_user")
MONEY_PASSWORD = os.environ.get("MONEY_PASSWORD", "my_basicauth_passwd")

LDAP_HOST = os.environ.get("LDAP_HOST", "ldap://127.0.0.1")
LDAP_USER = os.environ.get("LDAP_USER", "cn=admin,dc=flipdot,dc=org")
LDAP_PW = os.environ.get("LDAP_PW", "admin")

SENTRY_DSN = os.environ.get("SENTRY_DSN", "")

POSTGRES_CONNECTION_STRING = os.environ.get("POSTGRES_CONNECTION_STRING", "postgresql://drinks:drinks@postgres/drinks")

MAIL_FROM = os.environ.get("MAIL_FROM", "flipdot-noti@vega.uberspace.de")
MAIL_PW = os.environ.get("MAIL_PW", "pw")
MAIL_HOST = os.environ.get("MAIL_HOST", "vega.uberspace.de")
MAIL_PORT = os.environ.get("MAIL_PORT", 587)

FPS = 30

LOGLEVEL = "DEBUG"

# DEVELOPMENT VARIABLES #

# Prevent any mail from being sent.
NO_MAILS = True

# Send any mail to the user with the given id.
# Evaluates to MAIL_FROM by default.
FORCE_MAIL_TO_UID = "3"

# Do not fetch users from ldap.
# Use debug users instead.
USE_DEBUG_USERS = True

# ldap: do not save changes to users.
NO_USER_CHANGES = True
