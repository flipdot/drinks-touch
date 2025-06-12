import enum
import os
from datetime import timedelta
from pathlib import Path

import dotenv

dotenv.load_dotenv()

MONEY_URL = os.environ.get("MONEY_URL", "https://somewhere/x.json")
MONEY_USER = os.environ.get("MONEY_USER", "my_user")
MONEY_PASSWORD = os.environ.get("MONEY_PASSWORD", "my_basicauth_passwd")

DEBUG_LEVEL = os.environ.get("DEBUG_LEVEL", "False") in [
    "True",
    "true",
    "1",
    "yes",
]

_INFRAGELB = (246, 198, 0, 255)


class Color(enum.Enum):
    PRIMARY = _INFRAGELB
    GREY = (200, 200, 200, 255)
    DISABLED = (100, 100, 100, 255)
    ERROR = (255, 0, 0, 255)
    SUCCESS = (0, 255, 0, 255)
    BLACK = (0, 0, 0, 255)
    WHITE = (255, 255, 255, 255)
    BACKGROUND = (60, 60, 60, 255)
    NAVBAR_BACKGROUND = (5, 5, 5, 255)
    BUTTON_BACKGROUND = (0, 0, 0, 255)
    ORANGE = (255, 128, 0, 255)
    RED = (255, 0, 0, 255)
    GREEN = (0, 255, 0, 255)
    BLUE = (0, 0, 255, 255)
    MAGENTA = (255, 0, 255, 255)
    PURPLE = (128, 0, 255, 255)
    CYAN = (0, 255, 255, 255)


if bn := os.environ.get("BUILD_NUMBER"):
    BUILD_NUMBER = bn
else:
    BUILD_NUMBER = (
        os.popen("git rev-parse HEAD").read().strip() or "git is not available"
    )

GIT_REPO_AVAILABLE = (
    os.popen("git rev-parse --is-inside-work-tree").read().strip() == "true"
)
REPO_PATH = Path(__file__).parent.parent

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

ICAL_URL = os.environ.get(
    "ICAL_URL",
    "https://mail.flipdot.org/SOGo/dav/public/com@flipdot.org/Calendar/41-64A05800-5-1B5BE560.ics",
)
ICAL_FILE_PATH = REPO_PATH / "tmp/fd-calendar.ics"

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
    # 6 instead of 7 days, because the device might be booted only once a week,
    # and with 7 days, the user might not be notified for a week
    "weekly": timedelta(days=6),
    "instant and weekly": timedelta(days=6),
}

SCANNER_DEVICE_PATH = os.environ.get("SCANNER_DEVICE_PATH", "/dev/ttyACM0")

WEBSERVER_PORT = os.environ.get("WEBSERVER_PORT", 5002)

FPS = 60000000


class Font(enum.Enum):
    MONOSPACE = "drinks_touch/resources/fonts/DejaVuSansMono.ttf"
    SANS_SERIF = "drinks_touch/resources/fonts/DejaVuSans.ttf"


LOGLEVEL = os.environ.get("LOGLEVEL", "WARNING")

# DEVELOPMENT VARIABLES #

# Send any mail to the user with the given id.
# Evaluates to MAIL_FROM by default.
FORCE_MAIL_TO_UID = os.environ.get("FORCE_MAIL_TO_UID", None)

FULLSCREEN = os.environ.get("FULLSCREEN", "True") in ["True", "true", "1", "yes"]

# Yes, this is indeed the resolution of our shitty china display
SCREEN_WIDTH = 486
SCREEN_HEIGHT = 864
