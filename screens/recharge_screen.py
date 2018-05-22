# coding=utf-8
from functools import partial

from database.models.recharge_event import RechargeEvent
from database.storage import get_session
from elements.button import Button
from elements.image import Image
from elements.label import Label
from elements.progress import Progress
from env import monospace
from users.qr import make_sepa_qr
from .screen import Screen
from .screen_manager import ScreenManager
from .success import SuccessScreen


class RechargeScreen(Screen):
    def __init__(self, screen, user, **kwargs):
        super(RechargeScreen, self).__init__(screen)

        self.user = user

        self.objects.append(Button(
            self.screen,
            text = "BACK",
            pos=(30,30),
            font = monospace,
            click=self.back,
            size=30
        ))

        self.timeout = Progress(
            self.screen,
            pos=(200, 50),
            speed=1/30.0,
            on_elapsed=self.time_elapsed,
        )
        self.objects.append(self.timeout)
        self.timeout.start()

        qr_file = make_sepa_qr(20, self.user['name'], self.user['id'],
            pixel_width=7, border=4, color="yellow", bg="black")
        self.select_objects = [
            Button(
                self.screen,
                text='EUR 5',
                pos=(30, 300),
                size=30,
                click=partial(self.verify_payment, 5)
            ), Button(
                self.screen,
                text='EUR 10',
                pos=(250, 300),
                size=30,
                click=partial(self.verify_payment, 10)
            ), Button(
                self.screen,
                text='EUR 20',
                pos=(30, 400),
                size=30,
                click=partial(self.verify_payment, 20)
            ), Button(
                self.screen,
                text='EUR 50',
                pos=(250, 400),
                size=30,
                click=partial(self.verify_payment, 50)
            ), Label(
                self.screen,
                text = "Wirf Geld in die Kasse,",
                pos=(30, 100),
                size=50
            ), Label(
                self.screen,
                text = u"und drück den passenden",
                pos=(30, 150),
                size=50
            ), Label(
                self.screen,
                text="Knopf.",
                pos=(30, 200),
                size=50
            ), Image(
                self.screen,
                src=qr_file,
                pos=(30, 470),
                size=(350,380)
            )
        ]
        self.objects.extend(self.select_objects)

        self.verify_objects = [
            Label(
                self.screen,
                text="Hast du",
                pos=(30, 150),
                size=55
            ),
            Label(
                self.screen,
                text="in die Kasse geworfen?",
                pos=(30, 250),
                size=55
            ), Button(
                self.screen,
                text='Ja',
                pos=(250, 400),
                size=30,
                click=self.save_payment
            )
        ]
        self.verify_amount = Label(
            self.screen,
            text = "EUR X",
            pos=(30, 200),
            size=60
        )
        self.verify_objects.append(self.verify_amount)

    def back(self, param, pos):
        if self.verify_amount in self.objects:
            for o in self.verify_objects:
                if o in self.objects:
                    self.objects.remove(o)
            self.objects.extend(self.select_objects)
        else:
            screen_manager = ScreenManager.get_instance()
            screen_manager.go_back()

    def home(self):
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()

    def time_elapsed(self):
        self.home()

    def btn_home(self, param, pos):
        self.home()

    def verify_payment(self, amount, param, pos):
        amount = int(amount)
        self.payment_amount = amount
        for o in self.select_objects:
            if o in self.objects:
                self.objects.remove(o)
        self.objects.extend(self.verify_objects)
        self.verify_amount.text = "EUR " + str(amount)

    def save_payment(self, param, pos):
        session = get_session()
        ev = RechargeEvent(
            self.user['id'],
            'DISPLAY',
            self.payment_amount
        )
        session.add(ev)
        session.commit()

        screen_manager = ScreenManager.get_instance()
        screen_manager.set_active(
            SuccessScreen(self.screen, self.user, None,
                "EUR %s aufgeladen" % self.payment_amount, session))
        self.payment_amount = None
