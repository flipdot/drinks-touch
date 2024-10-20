import datetime
import logging

import config
from database.models.scan_event import ScanEvent
from database.storage import get_session
from drinks.drinks import get_by_ean
from drinks.drinks_manager import DrinksManager
from elements import RefreshIcon, SvgIcon, Progress, Label, Image, Button
from elements.hbox import HBox
from elements.vbox import VBox
from screens.new_id_screen import NewIDScreen
from screens.profile import ProfileScreen
from tasks import CheckForUpdatesTask
from users.users import Users
from .main import MainScreen
from .screen import Screen
from .screen_manager import ScreenManager
from sqlalchemy.sql import text

from .sync import SyncScreen

logger = logging.getLogger(__name__)


class WaitScanScreen(Screen):
    def __init__(self, screen):
        super(WaitScanScreen, self).__init__(screen)

        self.barcode_label = Label(
            pos=(60, 400),
        )

        self.scanned_info = [
            self.barcode_label,
            Button(
                pos=(50, 600),
                text="drink buchen",
                size=52,
                click_func=self.set_member,
            ),
            Button(
                pos=(50, 700),
                text="Nur Statistik",
                click_func=self.stat_drink,
            ),
            Button(
                pos=(350, 700),
                text="nope",
                click_func=self.btn_reset,
            ),
        ]
        self.empty_info = [
            Button(
                pos=(30, 655),
                size=45,
                text="Benutzer",
                click_func=self.set_member,
            ),
            Button(
                pos=(290, 690),
                size=15,
                text="Gutschein drucken",
                click_func=self.btn_new_id,
            ),
        ]

        self.objects.append(Image(pos=(30, 20)))

        self.objects.append(
            Label(
                text="Scanne dein Getränk",
                pos=(60, 240),
            )
        )
        self.objects.append(
            Label(
                text="oder deine ID-Card :)",
                pos=(70, 280),
            )
        )

        self.processing = Label(text="Moment bitte...", size=40, pos=(80, 350))
        self.processing.is_visible = False
        self.objects.append(self.processing)
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

        self.objects.append(
            VBox(
                elements=[
                    Label(
                        text="∑ = {}".format(total_balance_fmt),
                        size=25,
                    ),
                    Label(
                        text=f"Build: {config.BUILD_NUMBER}",
                        size=20,
                    ),
                ],
                pos=(5, 800),
                align_bottom=True,
            )
        )

        bottom_right_buttons = []

        if config.GIT_REPO_AVAILABLE:
            bottom_right_buttons.append(
                Button(
                    text=None,
                    inner=SvgIcon(
                        "drinks_touch/static/images/git.svg",
                        color=config.COLORS["disabled"],
                        height=36,
                    ),
                    color=config.COLORS["disabled"],
                    # click_func=lambda: ScreenManager.get_instance().set_active(
                    #     GitScreen(self.screen)
                    # ),
                ),
            )
        bottom_right_buttons.append(
            Button(
                text=None,
                click_func=lambda: ScreenManager.get_instance().set_active(
                    SyncScreen(self.screen)
                ),
                inner=RefreshIcon(),
            )
        )

        self.objects.append(
            HBox(
                pos=(480, 800),
                align_right=True,
                align_bottom=True,
                elements=bottom_right_buttons,
                right_to_left=True,
                gap=5,
                padding=(0, 5),
            )
        )
        if (
            CheckForUpdatesTask.newest_version_sha_short
            and CheckForUpdatesTask.newest_version_sha_short not in config.BUILD_NUMBER
        ):
            # make build number flash, show "Update available" when flashing
            self.objects.append(
                Label(
                    text=f"Update available: {CheckForUpdatesTask.newest_version_sha_short}",
                    size=25,
                    pos=(480, 800),
                    align_right=True,
                    align_bottom=True,
                    color=(0, 0, 0),
                    bg_color=(255, 255, 255),
                    padding=5,
                    blink_frequency=60,
                )
            )

        self.timeout = Progress(
            pos=(400, 500),
            size=100,
            speed=1 / 10.0,
            on_elapsed=self.time_elapsed,
        )
        self.objects.append(self.timeout)

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
        user = Users.get_by_id_card(barcode)
        if user:
            ScreenManager.get_instance().set_active(ProfileScreen(self.screen, user))
            self.processing.is_visible = False
            return
        drink = get_by_ean(barcode)
        DrinksManager.get_instance().set_selected_drink(drink)
        self.barcode_label.text = drink["name"]
        self.show_scanned_info(True)
        self.processing.is_visible = False
        self.timeout.start()

    def set_member(self):
        main = MainScreen(self.screen)
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

    def btn_new_id(self):
        new_id = NewIDScreen(self.screen)
        ScreenManager.get_instance().set_active(new_id)

    def reset(self, reset_drink=True):
        if reset_drink:
            DrinksManager.get_instance().set_selected_drink(None)
            self.timeout.stop()

        self.barcode_label.text = None
        self.show_scanned_info(False)
