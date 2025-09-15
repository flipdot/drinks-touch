import datetime
import functools
import logging
from dataclasses import dataclass
from pathlib import Path

import pytz
from dateutil.rrule import rrulestr

import config
from config import Color
from database.storage import with_db
from drinks.drinks_manager import DrinksManager
from elements import SvgIcon, Label, Button
from elements.hbox import HBox
from elements.vbox import VBox
from tasks import CheckForUpdatesTask
from .drink_scanned import DrinkScannedScreen
from .settings.main_screen import SettingsMainScreen
from .main import MainScreen
from .screen import Screen
from .screen_manager import ScreenManager

from .search_account import SearchAccountScreen
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

    @with_db
    def on_start(self, *args, **kwargs):
        if config.ICAL_FILE_PATH.exists():
            try:
                self.events = WaitScanScreen.load_events_from_ical(
                    config.ICAL_FILE_PATH
                )
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

        bottom_right_buttons = [
            Button(
                text=None,
                inner=SvgIcon(
                    "drinks_touch/resources/images/settings.svg",
                    color=config.Color.PRIMARY,
                    height=36,
                ),
                color=config.Color.PRIMARY,
                on_click=lambda: ScreenManager.instance.set_active(
                    SettingsMainScreen()
                ),
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
                            Label(
                                text=truncate(event.title, 24),
                                font=config.Font.MONOSPACE,
                                size=16,
                                color=event.fg_color,
                            ),
                        ],
                        gap=5,
                        bg_color=event.bg_color,
                        padding=(0, 11),
                    )
                    for event in self.events[::-1]
                ],
                pos=(0, 270),
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
                text="Veranstaltungen",
                pos=(110, 220),
                size=34,
            ),
            event_labels,
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
            and not config.BUILD_NUMBER == CheckForUpdatesTask.newest_version_sha_short
        ):
            # make build number flash, show "Update available" when flashing
            self.objects.append(
                Label(
                    font=config.Font.MONOSPACE,
                    text=f"Build: {CheckForUpdatesTask.newest_version_sha_short} <- Update available",
                    size=20,
                    pos=(5, config.SCREEN_HEIGHT - 5),
                    align_bottom=True,
                    color=config.Color.BACKGROUND,
                    bg_color=Color.PRIMARY,
                    padding=0,
                    blink_frequency=0.5,
                )
            )

        DrinksManager.instance.selected_barcode = None

    @staticmethod
    @functools.cache
    def load_events_from_ical(file_path: Path) -> list[FlipdotEvent]:
        with open(file_path, "r") as f:
            raw_ical = f.read()
        return WaitScanScreen.read_calendar(raw_ical)

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def load_calendar(raw_ical: str) -> Calendar:
        return Calendar(raw_ical)

    @staticmethod
    def read_calendar(raw_ical: str) -> list[FlipdotEvent]:
        events = []
        aware_now = pytz.utc.localize(datetime.datetime.utcnow())
        naive_now = aware_now.replace(tzinfo=None)

        cal = WaitScanScreen.load_calendar(raw_ical)

        for event in cal.events:
            now = aware_now
            first_occurrence = event.begin.datetime
            in_past = first_occurrence < now

            # Handle recurring events
            # find rrule string
            rule = None
            for content_line in event.extra:
                if content_line.name == "RRULE":
                    try:
                        rule = rrulestr(content_line.value, dtstart=first_occurrence)
                    except ValueError:
                        # For some reason, events that have an end date ("UNTIL"),
                        # that end date is not timezone-aware. Pass a timezone-naive timestamp
                        # and then make sure that the comparisons below are also naive.
                        rule = rrulestr(content_line.value, dtstart=event.begin.naive)
                        now = naive_now
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

        # Make offset-naive events timezone-aware, otherwise we can't sort them
        for event in events:
            if event.start.tzinfo is None:
                event.start = pytz.utc.localize(event.start)

        # Sort and limit to the latest 15 events
        # Make sure at least two events are in the past
        events.sort(key=lambda x: x.start, reverse=True)
        return events[:15]

    def on_barcode(self, barcode):
        if not barcode:
            self.goto(SearchAccountScreen())
            return
        self.goto(DrinkScannedScreen(barcode))
