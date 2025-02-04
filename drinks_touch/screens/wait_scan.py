import functools
import logging
import random

import config
from database.models import Account
from database.storage import get_session
from drinks.drinks_manager import DrinksManager
from elements import RefreshIcon, SvgIcon, Label, Button
from elements.hbox import HBox
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
from .tetris import TetrisScreen

logger = logging.getLogger(__name__)


class WaitScanScreen(Screen):
    idle_timeout = 0

    def __init__(self):
        super().__init__()
        self.scanned_info = []

    def on_start(self, *args, **kwargs):
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
                on_click=functools.partial(self.goto, TasksScreen()),
                inner=RefreshIcon(),
            ),
        ]

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
            VBox(
                [
                    Button(
                        text="T",
                        on_click=lambda: self.goto(
                            TetrisScreen(Account.query.all()[random.randint(0, 5)])
                        ),
                    ),
                ],
                pos=(50, 350),
            ),
            HBox(
                [
                    Button(
                        size=45,
                        text="Benutzer",
                        on_click=functools.partial(self.goto, MainScreen()),
                    ),
                    Button(
                        text=None,
                        inner=SvgIcon(
                            "drinks_touch/resources/images/magnifying-glass.svg",
                            height=53,
                        ),
                        on_click=functools.partial(self.goto, SearchAccountScreen()),
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
                    bg_color=(255, 255, 255),
                    padding=5,
                    blink_frequency=60,
                )
            )

        DrinksManager.instance.set_selected_drink(None)

    def on_barcode(self, barcode):
        if not barcode:
            # self.goto(SearchAccountScreen())
            self.goto(TetrisScreen(Account.query.all()[random.randint(0, 30)]))
            return
        self.goto(DrinkScannedScreen(barcode))
