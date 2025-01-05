import datetime
import functools
import logging

import config
from database.models import Account
from database.models.scan_event import ScanEvent
from database.storage import get_session
from drinks.drinks import get_by_ean
from drinks.drinks_manager import DrinksManager
from elements import RefreshIcon, SvgIcon, Progress, Label, Button
from elements.hbox import HBox
from elements.vbox import VBox
from screens.profile import ProfileScreen
from tasks import CheckForUpdatesTask
from .git.main_screen import GitMainScreen
from .main import MainScreen
from .screen import Screen
from .screen_manager import ScreenManager
from sqlalchemy.sql import text

from .tasks_screen import TasksScreen

logger = logging.getLogger(__name__)


class WaitScanScreen(Screen):
    idle_timeout = 0

    def __init__(self):
        super().__init__()
        self.barcode_label = None
        self.scanned_info = []
        self.empty_info = []
        self.processing = None
        self.timeout = None

    def on_start(self, *args, **kwargs):
        self.barcode_label = Label(
            pos=(60, 400),
        )

        self.scanned_info = [
            self.barcode_label,
            Button(
                pos=(50, 450),
                text="drink buchen",
                size=52,
                on_click=self.set_member,
            ),
            Button(
                pos=(50, 550),
                text="Nur Statistik",
                on_click=self.stat_drink,
            ),
            Button(
                pos=(350, 550),
                text="nope",
                on_click=self.btn_reset,
            ),
        ]
        self.empty_info = [
            Button(
                pos=(115, config.SCREEN_HEIGHT - 100),
                align_bottom=True,
                size=45,
                text="Benutzer",
                on_click=self.set_member,
            ),
        ]
        self.processing = Label(text="Moment bitte...", size=40, pos=(80, 350))
        self.processing.is_visible = False
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
                    "drinks_touch/static/images/git.svg",
                    color=color,
                    height=36,
                ),
                color=color,
                on_click=(
                    (lambda: ScreenManager.get_instance().set_active(GitMainScreen()))
                    if config.GIT_REPO_AVAILABLE
                    else None
                ),
            ),
            Button(
                on_click=functools.partial(self.goto, TasksScreen()),
                inner=RefreshIcon(),
            ),
        ]
        self.timeout = Progress(
            pos=(400, 500),
            size=100,
            speed=1 / 10.0,
            on_elapsed=self.time_elapsed,
        )

        self.objects = [
            SvgIcon(
                "drinks_touch/resources/images/flipdot.svg",
                width=400,
                pos=(40, 20),
            ),
            Label(
                text="Scanne dein Getränk",
                pos=(60, 240),
            ),
            Label(
                text="oder deine ID-Card :)",
                pos=(70, 280),
            ),
            self.processing,
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
                bottom_right_buttons,
                pos=(config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
                align_right=True,
                align_bottom=True,
                gap=5,
                padding=(5, 5),
            ),
            self.timeout,
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
                    pos=(480, 800),
                    align_right=True,
                    align_bottom=True,
                    color=config.Color.BLACK,
                    bg_color=(255, 255, 255),
                    padding=5,
                    blink_frequency=60,
                )
            )

        for o in self.scanned_info + self.empty_info:
            self.objects.append(o)

        self.reset()

    def time_elapsed(self):
        self.reset()

    def show_scanned_info(self, show):
        for o in self.scanned_info:
            o.is_visible = show
        for o in self.empty_info:
            o.is_visible = not show

    def on_barcode(self, barcode):
        if not barcode:
            return
        self.processing.text = f"Gescannt: {barcode}"
        self.processing.is_visible = True
        account = Account.query.filter(Account.id_card == barcode).first()
        if account:
            ScreenManager.get_instance().set_active(ProfileScreen(account))
            self.processing.is_visible = False
            return
        drink = get_by_ean(barcode)
        DrinksManager.get_instance().set_selected_drink(drink)
        self.barcode_label.text = drink["name"]
        self.show_scanned_info(True)
        self.processing.is_visible = False
        self.timeout.start()

    def set_member(self):
        main = MainScreen()
        ScreenManager.get_instance().set_active(main)
        self.reset(False)

    def stat_drink(self):
        drink = DrinksManager.get_instance().get_selected_drink()
        if drink:
            session = get_session()
            ev = ScanEvent(drink["ean"], 0, datetime.datetime.now())
            session.add(ev)
            session.commit()
            DrinksManager.get_instance().set_selected_drink(None)
        self.reset()

    def btn_reset(self):
        self.reset()

    def reset(self, reset_drink=True):
        if reset_drink:
            DrinksManager.get_instance().set_selected_drink(None)
            self.timeout.stop()

        self.barcode_label.text = None
        self.show_scanned_info(False)
