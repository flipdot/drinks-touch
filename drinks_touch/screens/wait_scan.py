import datetime

from database.models.scan_event import ScanEvent
from database.storage import get_session
from drinks.drinks import get_by_ean
from drinks.drinks_manager import DrinksManager
from elements.button import Button
from elements.image import Image
from elements.label import Label
from elements.progress import Progress
from screens.new_id_screen import NewIDScreen
from screens.profile import ProfileScreen
from users.users import Users
from .main import MainScreen
from .screen import Screen
from .screen_manager import ScreenManager


class WaitScanScreen(Screen):
    def __init__(self, screen):
        super(WaitScanScreen, self).__init__(screen)

        self.barcode_label = Label(
            self.screen,
            pos=(60, 400),
        )

        self.scanned_info = [
            self.barcode_label,
            Button(
                self.screen,
                pos=(50, 600),
                text="drink buchen",
                size=52,
                click_func=self.set_member
            ),
            Button(
                self.screen,
                pos=(50, 700),
                text="Nur Statistik",
                click_func=self.stat_drink
            ),
            Button(
                self.screen,
                pos=(350, 700),
                text="nope",
                click_func=self.btn_reset
            )
        ]
        self.empty_info = [
            Button(
                self.screen,
                pos=(30, 700),
                text="Benutzer",
                click_func=self.set_member
            ),
            Button(
                self.screen,
                pos=(210, 700),
                text="Geld einwerfen",
                click_func=self.btn_new_id
            )
        ]

        self.objects.append(Image(
            self.screen,
            pos=(30, 20)
        ))

        self.objects.append(Label(
            self.screen,
            text=u"Scanne dein Getränk",
            pos=(60, 240),
        ))
        self.objects.append(Label(
            self.screen,
            text=u"oder deine ID-Card :)",
            pos=(70, 280),
        ))

        self.processing = Label(
            self.screen,
            text="Moment bitte...",
            size=40,
            pos=(80, 350)
        )
        self.processing.is_visible = False
        self.objects.append(self.processing)

        self.objects.append(Label(
            self.screen,
            text="Gesamtguthaben aller Member: -XXX,XX€",
            size=25,
            pos=(125, 755)
        ))

        self.timeout = Progress(
            self.screen,
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
        self.processing.is_visible = True
        user = Users.get_by_id_card(barcode)
        if user:
            ScreenManager.get_instance().set_active(
                ProfileScreen(self.screen, user)
            )
            self.processing.is_visible = False
            return
        drink = get_by_ean(barcode)
        DrinksManager.get_instance().set_selected_drink(drink)
        self.barcode_label.text = drink['name']
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
            ev = ScanEvent(
                drink['ean'],
                0,
                datetime.datetime.now()
            )
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

    @staticmethod
    def back():
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()
