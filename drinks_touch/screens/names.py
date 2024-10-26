import functools
import math

from config import FONTS
from database.models import Account
from elements.button import Button
from elements.label import Label
from elements.progress import Progress
from screens.profile import ProfileScreen
from .screen import Screen
from .screen_manager import ScreenManager


class NamesScreen(Screen):
    def __init__(self, screen, char):
        super().__init__(screen)
        self.char = char
        self.timeout = None

    def on_start(self, *args, **kwargs):
        self.objects = []
        self.objects.append(
            Button(
                text="BACK",
                pos=(30, 30),
                on_click=self.back,
                font=FONTS["monospace"],
                size=30,
            )
        )

        self.timeout = Progress(
            pos=(200, 50),
            speed=1 / 15.0,
            on_elapsed=self.time_elapsed,
        )
        self.objects.append(self.timeout)
        self.timeout.start()

        self.objects.append(
            Label(
                text="Wer bist du?",
                pos=(20, 110),
            )
        )

        # users = list(Users.get_all(filters=["uid=" + self.char + "*"]))
        accounts = (
            Account.query.filter(Account.name.ilike(self.char + "%"))
            .order_by(Account.name)
            .all()
        )

        btns_y = 7
        num_cols = int(math.ceil(len(accounts) / float(btns_y)))
        for i, account in enumerate(accounts):
            xoff, yoff = 30, 190
            btn_ypos = 90
            i_y = i % btns_y
            i_x = i // btns_y
            x = i_x * (self.screen.get_width() / num_cols)
            y = i_y * btn_ypos
            self.objects.append(
                Button(
                    text=account.name,
                    pos=(xoff + x, y + yoff),
                    on_click=functools.partial(
                        self.goto, ProfileScreen(self.screen, account)
                    ),
                    padding=20,
                )
            )
            i += 1

    @staticmethod
    def home():
        ScreenManager.get_instance().set_default()

    def time_elapsed(self):
        self.home()

    def on_barcode(self, barcode):
        if not barcode:
            return
        account = Account.query.filter(Account.id_card == barcode).first()
        if account:
            self.goto(ProfileScreen(self.screen, account))
