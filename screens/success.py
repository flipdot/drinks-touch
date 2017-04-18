# coding=utf-8
import pygame
import os

from elements.label import Label
from elements.button import Button
from elements.image import Image
from elements.progress import Progress

from drinks.drinks_manager import DrinksManager

from users.users import Users

from .screen import Screen

from .screen_manager import ScreenManager

class SuccessScreen(Screen):
    def __init__(self, screen, user, session, **kwargs):
        super(SuccessScreen, self).__init__(screen)

        self.user = user

        self.objects.append(Label(
            self.screen,
            text='Erfolgeich erfasst!',
            pos=(30, 120),
            size=70
        ))
        self.objects.append(Label(
            self.screen,
            text='Verbleibendes Guthaben: ',
            pos=(30, 190)
        ))
        self.objects.append(Label(
            self.screen,
            text=str(Users.get_balance(self.user['id'], session=session))+' EUR',
            pos=(50, 250)
        ))

        self.objects.append(Button(
            self.screen,
            text='OK',
            pos=(50, 600),
            size=50,
            click=self.btn_home
        ))

        self.progress = Progress(
            self.screen,
            pos=(400, 500),
            size=80,
            on_elapsed=self.home
        )
        self.objects.append(self.progress)
        self.progress.start()
        balance = Users.get_balance(user['id'])
        if balance > 0:
            sound = "smb_coin.wav"
        else:
            sound = "smb_bowserfalls.wav"
        os.system("ssh -o StrictHostKeyChecking=no pi@pixelfun aplay sounds/%s >/dev/null 2>&1 &" % sound)

    def home(self):
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()

    def btn_home(self, param, pos):
        self.home()
