from functools import partial

from config import Font
from database.models import Account
from database.models.recharge_event import RechargeEvent
from database.storage import get_session
from elements.button import Button
from elements.image import Image
from elements.label import Label
from elements.progress import Progress
from users.qr import make_sepa_qr
from .screen import Screen
from .screen_manager import ScreenManager
from .success import SuccessScreen


class RechargeScreen(Screen):
    def __init__(self, account: Account):
        super().__init__()

        self.account = account
        self.payment_amount = 0
        self.timeout = None
        self.select_objects = []
        self.verify_objects = []
        self.verify_amount = None

    def on_start(self, *args, **kwargs):
        self.objects = []
        self.objects.append(
            Button(
                text="BACK",
                pos=(30, 30),
                font=Font.MONOSPACE,
                on_click=self.back,
                size=30,
            )
        )

        self.timeout = Progress(
            pos=(200, 50),
            speed=1 / 30.0,
            on_elapsed=self.time_elapsed,
        )
        self.objects.append(self.timeout)
        self.timeout.start()

        qr_file = make_sepa_qr(
            20,
            self.account.name,
            self.account.ldap_id,
            pixel_width=7,
            border=4,
            color="black",
            bg="yellow",
        )
        self.select_objects = [
            Button(
                text="EUR 5",
                pos=(30, 250),
                size=30,
                on_click=partial(self.verify_payment, 5),
            ),
            Button(
                text="EUR 10",
                pos=(250, 250),
                size=30,
                on_click=partial(self.verify_payment, 10),
            ),
            Button(
                text="EUR 20",
                pos=(30, 350),
                size=30,
                on_click=partial(self.verify_payment, 20),
            ),
            Button(
                text="EUR 50",
                pos=(250, 350),
                size=30,
                on_click=partial(self.verify_payment, 50),
            ),
            Label(text="Wirf Geld in die Kasse,", pos=(30, 100), size=40),
            Label(text="und drück den passenden", pos=(30, 150), size=40),
            Label(text="Knopf.", pos=(30, 200), size=40),
            Image(src=qr_file, pos=(70, 420), size=(300, 330)),
        ]
        self.objects.extend(self.select_objects)

        self.verify_objects = [
            Label(text="Hast du", pos=(30, 150), size=35),
            Label(text="in die Kasse geworfen?", pos=(30, 250), size=35),
            Button(
                text="Ja",
                pos=(250, 400),
                size=30,
                on_click=self.save_payment,
            ),
        ]
        self.verify_amount = Label(text="EUR X", pos=(30, 200), size=50)
        self.verify_objects.append(self.verify_amount)

    def back(self):
        if self.verify_amount in self.objects:
            for o in self.verify_objects:
                if o in self.objects:
                    self.objects.remove(o)
            self.objects.extend(self.select_objects)
        else:
            super().back()

    @staticmethod
    def home():
        from .screen_manager import ScreenManager

        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()

    def time_elapsed(self):
        self.home()

    def btn_home(self):
        self.home()

    def verify_payment(self, amount):
        amount = int(amount)
        self.payment_amount = amount
        for o in self.select_objects:
            if o in self.objects:
                self.objects.remove(o)
        self.objects.extend(self.verify_objects)
        self.verify_amount.text = "EUR " + str(amount)

    def save_payment(self):
        session = get_session()
        ev = RechargeEvent(self.account.ldap_id, "DISPLAY", self.payment_amount)
        session.add(ev)
        session.commit()

        screen_manager = ScreenManager.get_instance()
        screen_manager.set_active(
            SuccessScreen(
                self.account,
                None,
                "EUR %s aufgeladen" % self.payment_amount,
                session,
            )
        )
        self.payment_amount = None
