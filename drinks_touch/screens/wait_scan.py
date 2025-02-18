import datetime
import functools
import logging
from dataclasses import dataclass

import pytz
from dateutil.rrule import rrulestr

import config
from config import Color
from database.storage import get_session
from drinks.drinks_manager import DrinksManager
from elements import RefreshIcon, SvgIcon, Label, Button
from elements.hbox import HBox
from elements.spacer import Spacer
from elements.vbox import VBox
from tasks import CheckForUpdatesTask
from .drink_scanned import DrinkScannedScreen
from .git.main_screen import GitMainScreen
from .main import MainScreen
from .screen import Screen
from .screen_manager import ScreenManager
from sqlalchemy.sql import text

from .search_account import SearchAccountScreen
from .tasks_screen import TasksScreen
from ics import Calendar

logger = logging.getLogger(__name__)


@dataclass
class FlipdotEvent:
    title: str
    start: datetime.datetime
    color: Color
    recurring: bool = False
    # description: str

    @property
    def today(self) -> bool:
        return self.start.date() == datetime.datetime.now().date()

    @property
    def fg_color(self) -> Color:
        return Color.BLACK if self.today else self.color

    @property
    def bg_color(self) -> Color | None:
        return Color.PRIMARY if self.today else None


def truncate(text: str, length: int) -> str:
    text = text.strip()  # remove leading/trailing whitespace
    if len(text) <= length + 1:
        return text.rjust(length)
    return text[: length - 10] + "…" + text[-10:]


class WaitScanScreen(Screen):
    idle_timeout = 0

    def __init__(self):
        super().__init__()
        self.events: list[FlipdotEvent] = []

    def on_start(self, *args, **kwargs):
        if config.ICAL_FILE_PATH.exists():
            with open(config.ICAL_FILE_PATH, "r") as f:
                raw_ical = f.read()
            try:
                self.events = self.read_calendar(raw_ical)
            except Exception:
                logger.exception("Error while reading calendar")
                self.events = [
                    FlipdotEvent(
                        title="Error reading calendar",
                        start=datetime.datetime.now(),
                        color=Color.RED,
                    ),
                    FlipdotEvent(
                        title=config.ICAL_URL,
                        start=datetime.datetime.now(),
                        color=Color.RED,
                    ),
                    FlipdotEvent(
                        title=str(config.ICAL_FILE_PATH),
                        start=datetime.datetime.now(),
                        color=Color.RED,
                    ),
                ]

        sql = text(
            """
            SELECT SUM(amount) - (
                SELECT COUNT(*) FROM "scanevent"
                 WHERE "user_id" NOT LIKE 'geld%' AND "user_id" != '0'
                ) AS Gesamtguthaben
            FROM "rechargeevent" WHERE "user_id" NOT LIKE 'geld%';"""
        )
        try:
            total_balance = get_session().execute(sql).scalar() or 0
            total_balance_fmt = "{:.02f}€".format(total_balance)
        except Exception:
            logger.exception("sql error while getting total money amount")
            total_balance_fmt = "(SQL Error)"

        color = (
            config.Color.PRIMARY if config.GIT_REPO_AVAILABLE else config.Color.DISABLED
        )
        bottom_right_buttons = [
            Button(
                text=None,
                inner=SvgIcon(
                    "drinks_touch/resources/images/git.svg",
                    color=color,
                    height=36,
                ),
                color=color,
                on_click=(
                    (lambda: ScreenManager.instance.set_active(GitMainScreen()))
                    if config.GIT_REPO_AVAILABLE
                    else None
                ),
            ),
            Button(
                on_click=lambda: self.goto(TasksScreen()),
                inner=RefreshIcon(),
            ),
        ]

        if self.events:
            event_labels = VBox(
                [
                    HBox(
                        [
                            Label(
                                text=event.start.strftime("%a, %Y-%m-%d %H:%M"),
                                font=config.Font.MONOSPACE,
                                size=16,
                                color=event.fg_color,
                            ),
                            SvgIcon(
                                "drinks_touch/resources/images/rotate-clockwise.svg",
                                width=14,
                                padding=(2, 0),
                                visible=event.recurring,
                                color=event.fg_color,
                            ),
                            Spacer(width=14, visible=not event.recurring),
                            Label(
                                text=truncate(event.title, 24),
                                font=config.Font.MONOSPACE,
                                size=16,
                                color=event.fg_color,
                            ),
                        ],
                        gap=5,
                        bg_color=event.bg_color,
                    )
                    for event in self.events[::-1]
                ],
                pos=(10, 270),
            )
        else:
            event_labels = Label(  # noqa: F841
                text="Keine anstehenden Events", pos=(10, 270)
            )

        self.objects = [
            SvgIcon(
                "drinks_touch/resources/images/flipdot.svg",
                width=400,
                pos=(40, 20),
            ),
            Label(
                text="Komm zu unseren Veranstaltungen:",
                pos=(10, 230),
                size=24,
            ),
            event_labels,
            Label(
                text="Mehr Infos unter https://flipdot.org",
                pos=(10, config.SCREEN_HEIGHT - 220),
                size=24,
            ),
            VBox(
                [
                    Label(
                        text="∑ = {}".format(total_balance_fmt),
                        size=25,
                    ),
                    Label(
                        text=f"Build: {config.BUILD_NUMBER}",
                        size=20,
                    ),
                ],
                pos=(0, config.SCREEN_HEIGHT),
                padding=(5, 5),
                align_bottom=True,
            ),
            HBox(
                [
                    Button(
                        size=45,
                        text="Benutzer",
                        on_click=lambda: self.goto(MainScreen()),
                    ),
                    Button(
                        text=None,
                        inner=SvgIcon(
                            "drinks_touch/resources/images/magnifying-glass.svg",
                            height=53,
                            color=config.Color.PRIMARY,
                        ),
                        on_click=lambda: self.goto(SearchAccountScreen()),
                    ),
                ],
                pos=(config.SCREEN_WIDTH - 80, config.SCREEN_HEIGHT - 100),
                align_bottom=True,
                align_right=True,
            ),
            HBox(
                bottom_right_buttons,
                pos=(config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
                align_right=True,
                align_bottom=True,
                gap=5,
                padding=(5, 5),
            ),
        ]

        if (
            CheckForUpdatesTask.newest_version_sha_short
            and CheckForUpdatesTask.newest_version_sha_short not in config.BUILD_NUMBER
        ):
            # make build number flash, show "Update available" when flashing
            self.objects.append(
                Label(
                    text=f"Update available: {CheckForUpdatesTask.newest_version_sha_short}",
                    size=15,
                    pos=(config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
                    align_right=True,
                    align_bottom=True,
                    color=config.Color.BLACK,
                    bg_color=Color.WHITE,
                    padding=0,
                    blink_frequency=60,
                )
            )

        DrinksManager.instance.set_selected_drink(None)

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def load_calendar(raw_ical: str) -> Calendar:
        return Calendar(raw_ical)

    @staticmethod
    def read_calendar(raw_ical: str) -> list[FlipdotEvent]:
        events = []
        now = pytz.utc.localize(datetime.datetime.utcnow())

        cal = WaitScanScreen.load_calendar(raw_ical)

        for event in cal.events:
            first_occurrence = event.begin.datetime
            in_past = first_occurrence < now

            # Handle recurring events
            # find rrule string
            rule = None
            for content_line in event.extra:
                if content_line.name == "RRULE":
                    rule = rrulestr(content_line.value, dtstart=first_occurrence)
                    break

            if rule:
                # Recurring events
                # add next event
                if occurrence := rule.after(now, inc=True):
                    events.append(
                        FlipdotEvent(
                            title=event.name,
                            start=occurrence,
                            color=Color.PRIMARY,
                            recurring=True,
                        )
                    )
                # add past event
                if occurrence := rule.before(now, inc=True):
                    events.append(
                        FlipdotEvent(
                            title=event.name,
                            start=occurrence,
                            color=Color.DISABLED,
                            recurring=True,
                        )
                    )
            else:
                # Non-recurring events
                events.append(
                    FlipdotEvent(
                        title=event.name,
                        start=first_occurrence,
                        color=Color.DISABLED if in_past else Color.PRIMARY,
                        recurring=bool(rule),
                    )
                )

        # Sort and limit to the latest 15 events
        # Make sure at least two events are in the past
        events.sort(key=lambda x: x.start, reverse=True)
        return events[:15]

    def on_barcode(self, barcode):
        if not barcode:
            self.goto(SearchAccountScreen())
            return
        self.goto(DrinkScannedScreen(barcode))
