import datetime
import functools

from sqlalchemy.sql import text

from config import FONTS
from database.models import Account
from database.models.scan_event import ScanEvent
from database.storage import get_session
from drinks.drinks import get_by_ean
from drinks.drinks_manager import DrinksManager
from elements.button import Button
from elements.label import Label
from elements.progress import Progress
from screens.recharge_screen import RechargeScreen
from users.users import Users
from .id_card_screen import IDCardScreen
from .screen import Screen
from .screen_manager import ScreenManager
from .success import SuccessScreen


class ProfileScreen(Screen):
    def __init__(self, screen, account: Account):
        super().__init__(screen)

        self.account = account
        self.label_verbrauch = None
        self.label_aufladungen = None
        self.processing = None
        self.timeout = None
        self.drink_info = None
        self.zuordnen = None
        self.btn_aufladungen = None
        self.btn_drinks = None
        self.btn_abbrechen = None
        self.btn_aufladen = None
        self.elements_aufladungen = []
        self.elements_drinks = []

    def on_start(self, *args, **kwargs):
        self.objects = []
        self.objects.append(
            Button(
                text="BACK",
                pos=(30, 30),
                font=FONTS["monospace"],
                on_click=self.back,
            )
        )

        self.objects.append(
            Button(
                text="ID card",
                pos=(340, 30),
                font=FONTS["monospace"],
                on_click=self.id_card,
            )
        )

        self.objects.append(
            Label(
                text=self.account.name,
                pos=(30, 120),
                size=40,
                max_width=335 - 30 - 10,  # balance.x - self.x - margin
            )
        )

        self.objects.append(
            Label(
                text="Guthaben",
                pos=(330, 120),
                size=20,
            )
        )

        self.label_verbrauch = Label(
            text="Bisheriger Verbrauch:",
            pos=(30, 180),
            size=15,
        )
        self.label_aufladungen = Label(
            text="Aufladungen:",
            pos=(30, 180),
            size=15,
        )

        self.processing = Label(
            text="Moment bitte...",
            size=20,
            pos=(150, 750),
        )
        self.processing.is_visible = False
        self.objects.append(self.processing)

        self.timeout = Progress(
            pos=(200, 50),
            speed=1 / 30.0,
            on_elapsed=self.time_elapsed,
        )
        self.objects.append(self.timeout)
        self.timeout.start()

        drink = DrinksManager.get_instance().get_selected_drink()
        self.drink_info = Label(
            text=drink["name"] if drink else "",
            size=30,
            pos=(30, 630),
        )

        self.zuordnen = Button(
            text="Trinken",
            pos=(30, 690),
            size=40,
            on_click=self.save_drink,
        )
        self.btn_aufladungen = Button(
            text="Aufladungen",
            pos=(30, 700),
            on_click=self.show_aufladungen,
        )
        self.btn_drinks = Button(
            text="Buchungen",
            pos=(20, 700),
            on_click=self.show_drinks,
        )
        self.btn_abbrechen = Button(
            text="Abbrechen",
            pos=(290, 700),
            size=20,
            on_click=self.btn_home,
        )
        self.btn_aufladen = Button(
            text="Jetzt Aufladen",
            pos=(210, 700),
            size=20,
            on_click=functools.partial(
                self.goto, RechargeScreen(self.screen, self.account)
            ),
        )

        self.elements_aufladungen = [
            self.btn_drinks,
            self.label_aufladungen,
            self.btn_aufladen,
        ]
        self.elements_drinks = [self.label_verbrauch, self.btn_abbrechen]
        if drink:
            self.elements_drinks.extend([self.zuordnen, self.drink_info])
        else:
            self.elements_drinks.append(self.btn_aufladungen)

        self.objects.append(
            Label(text=str(self.account.balance), pos=(335, 145), size=40)
        )

        drinks = self.get_stats()
        for i, drinks in enumerate(drinks):
            x = 30
            if i == 11:
                self.elements_drinks.append(Label(text="...", pos=(x, 210 + (i * 35))))
                continue
            if i > 11:
                continue
            ean_text = get_by_ean(drinks["name"])["name"]
            count_width = 80
            margin_right = 10
            self.elements_drinks.append(
                Label(
                    text=ean_text,
                    pos=(x, 210 + (i * 35)),
                    max_width=480 - x - margin_right - count_width,
                )
            )
            self.elements_drinks.append(
                Label(
                    text=str(drinks["count"]),
                    align_right=True,
                    pos=(480 - margin_right, 210 + (i * 35)),
                    max_width=count_width,
                )
            )

        self.objects.extend(self.elements_drinks)

        self.render_aufladungen()

    def render_aufladungen(self):
        # aufladungen = Users.get_recharges(self.user["id"], limit=12)
        aufladungen = self.account.get_recharges().limit(12).all()
        y = 210
        prev_date = None
        for i, aufladung in enumerate(aufladungen):
            x = 30
            if y + 45 * 2 >= self.btn_drinks.pos[1]:
                self.elements_aufladungen.append(Label(text="...", pos=(x, y)))
                break
            date = aufladung.timestamp.strftime("%a, %-d.%-m.%Y")
            time = aufladung.timestamp.strftime("%H:%M")
            time_text = time
            helper = aufladung.helper_user_id
            if helper:
                if helper == "SEPA":
                    time_text += " mit SEPA"
                elif helper == "DISPLAY":
                    time_text += " mit DISPLAY"
                else:
                    user = Users.get_by_id(aufladung.helper_user_id)
                    if user:
                        helper = user["name"]
                        time_text += " mit " + helper
            if date != prev_date:
                prev_date = date
                self.elements_aufladungen.append(
                    Label(text=date, size=30, pos=(x, y + 15))
                )
                y += 45
            count_width = 120
            margin_right = 10
            self.elements_aufladungen.append(
                Label(
                    text=time_text,
                    pos=(x + 10, y),
                    size=25,
                    max_width=480 - x - margin_right - count_width,
                )
            )
            self.elements_aufladungen.append(
                Label(
                    text=str(aufladung.amount),
                    align_right=True,
                    pos=(480 - margin_right, y - 5),
                    max_width=count_width,
                    size=25,
                )
            )
            y += 35

    def save_drink(self):
        session = get_session()
        drink = DrinksManager.get_instance().get_selected_drink()
        if not drink:
            return
        ev = ScanEvent(drink["ean"], self.account.ldap_id, datetime.datetime.now())
        session.add(ev)
        session.commit()
        DrinksManager.get_instance().set_selected_drink(None)
        Users.delete_if_nomoney(
            {
                "path": self.account.ldap_path,
                "id": self.account.ldap_id,
            }
        )

        screen_manager = ScreenManager.get_instance()
        screen_manager.set_active(
            SuccessScreen(
                self.screen,
                self.account,
                drink,
                "getrunken: %s" % drink["name"],
                session,
            )
        )

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
        self.drink_info.text = drink["name"]
        if self.zuordnen not in self.objects:
            self.objects.extend([self.zuordnen, self.drink_info])
        if self.btn_aufladungen in self.objects:
            self.objects.remove(self.btn_aufladungen)
        if self.btn_drinks in self.objects:
            self.objects.remove(self.btn_drinks)
        self.processing.is_visible = False
        self.timeout.start()

    def id_card(self):
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_active(IDCardScreen(self.screen, self.account))

    @staticmethod
    def home():
        from .screen_manager import ScreenManager

        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()

    def btn_home(self):
        self.home()

    def time_elapsed(self):
        self.home()

    def show_aufladungen(self):
        for d in self.elements_drinks:
            self.objects.remove(d)
        self.objects.extend(self.elements_aufladungen)
        self.timeout.start()

    def show_drinks(self):
        for d in self.elements_aufladungen:
            self.objects.remove(d)
        self.objects.extend(self.elements_drinks)
        self.timeout.start()

    def get_stats(self):
        session = get_session()
        sql = text(
            """
            SELECT COUNT(*) as count, barcode as name
            FROM scanevent
            WHERE user_id = :userid
            GROUP BY barcode
            ORDER by count DESC
        """
        )
        result = (
            session.connection()
            .execute(sql, {"userid": self.account.ldap_id})
            .fetchall()
        )

        return [{"count": x[0], "name": x[1]} for x in result]
