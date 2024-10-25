import functools
import math

from config import FONTS
from elements.button import Button
from elements.label import Label
from elements.progress import Progress
from screens.profile import ProfileScreen
from users.users import Users
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

        users = list(Users.get_all(filters=["uid=" + self.char + "*"]))

        btns_y = 7
        num_cols = int(math.ceil(len(users) / float(btns_y)))
        for i, user in enumerate(users):
            xoff, yoff = 30, 190
            btn_ypos = 90
            i_y = i % btns_y
            i_x = i // btns_y
            x = i_x * (self.screen.get_width() / num_cols)
            y = i_y * btn_ypos
            self.objects.append(
                Button(
                    text=user["name"],
                    pos=(xoff + x, y + yoff),
                    on_click=functools.partial(self.switch_to_screen, user),
                    padding=20,
                )
            )
            i += 1

    def switch_to_screen(self, param):
        ScreenManager.get_instance().set_active(ProfileScreen(self.screen, param))

    @staticmethod
    def home():
        ScreenManager.get_instance().set_default()

    def time_elapsed(self):
        self.home()

    def on_barcode(self, barcode):
        if not barcode:
            return
        user = Users.get_by_id_card(barcode)
        if user:
            ScreenManager.get_instance().set_active(ProfileScreen(self.screen, user))
