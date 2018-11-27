# coding=utf-8

import math

from elements.button import Button
from elements.label import Label
from elements.progress import Progress
from env import monospace
from screens.profile import ProfileScreen
from users.users import Users
from .screen import Screen
from .screen_manager import ScreenManager


class NamesScreen(Screen):
    def __init__(self, screen, char, **kwargs):
        super(NamesScreen, self).__init__(screen)

        self.char = char

        self.objects.append(Button(
            self.screen,
            text="BACK",
            pos=(30, 30),
            click=self.back,
            font=monospace,
            size=30
        ))

        self.timeout = Progress(
            self.screen,
            pos=(200, 50),
            speed=1 / 15.0,
            on_elapsed=self.time_elapsed,
        )
        self.objects.append(self.timeout)
        self.timeout.start()

        self.objects.append(Label(
            self.screen,
            text='Wer bist du?',
            pos=(20, 110),
        ))

        users = Users.get_all(self.char)

        btns_y = 7
        num_cols = int(math.ceil(len(users) / float(btns_y)))
        for i, user in enumerate(users):
            padding = 20
            xoff, yoff = 30, 190
            btn_ypos = 90
            i_y = i % btns_y
            i_x = i // btns_y
            x = i_x * (screen.get_width() / num_cols)
            y = i_y * btn_ypos
            self.objects.append(Button(
                self.screen,
                text=user["name"],
                pos=(xoff + x, y + yoff),
                click=self.switch_to_screen,
                click_param=user,
                padding=padding
            ))
            i += 1

    @staticmethod
    def back(param, pos):
        ScreenManager.get_instance().go_back()

    def switch_to_screen(self, param, pos):
        ScreenManager.get_instance().set_active(
            ProfileScreen(self.screen, param)
        )

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
            ScreenManager.get_instance().set_active(
                ProfileScreen(self.screen, user)
            )
