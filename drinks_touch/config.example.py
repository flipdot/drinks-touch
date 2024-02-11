MONEY_URL = "https://somewhere/x.json"
MONEY_USER = "my_user"
MONEY_PASSWORD = "my_basicauth_passwd"

LDAP_HOST = "ldap://ldap.example.com"
LDAP_USER = "cn=admin,dc=flipdot,dc=org"
LDAP_PW = "admin"

SENTRY_DSN = ""

# POSTGRES_CONNECTION_STRING = "postgresql://postgres:postgres@127.0.0.1/drinks"
POSTGRES_CONNECTION_STRING = "postgresql://postgres:postgres@postgres/drinks"  # Docker

MAIL_FROM = "flipdot-noti@vega.uberspace.de"
MAIL_PW = "pw"
MAIL_HOST = "vega.uberspace.de"
MAIL_PORT = 587

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
