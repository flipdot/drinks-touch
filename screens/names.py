# coding=utf-8
import pygame

from elements.label import Label
from elements.button import Button
from elements.progress import Progress

from users.users import Users

from .screen import Screen
from screens.enter_pin import EnterPinScreen
from screens.profile import ProfileScreen

from env import monospace

class NamesScreen(Screen):
    def __init__(self, screen, char, **kwargs):
        super(NamesScreen, self).__init__(screen)

        self.char = char

        self.objects.append(Button(
            self.screen,
            text = "BACK",
            pos=(30,30),
            click=self.back,
            font = monospace,
            size=30
        ))

        self.timeout = Progress(
            self.screen,
            pos=(200, 50),
            speed=1/15.0,
            on_elapsed=self.time_elapsed,
        )
        self.objects.append(self.timeout)
        self.timeout.start()

        self.objects.append(Label(
            self.screen,
            text ='Wer bist du?',
            pos=(20, 130),
        ))

        users = Users.get_all(self.char)

        i = 0
        for user in users:
            self.objects.append(Button(
                self.screen,
                text = user["name"],
                pos=(30,190 + (i * 80)),
                click=self.switch_to_screen,
                click_param=user,
                padding=20
            ))
            i += 1

    def back(self, param, pos):
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.go_back()

    def switch_to_screen(self, param, pos):
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_active(
            ProfileScreen(self.screen, param)
        )

    def home(self):
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance().set_default()

    def time_elapsed(self):
        self.home()
