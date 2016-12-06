# coding=utf-8
import pygame
import datetime

from elements.label import Label
from elements.button import Button
from elements.image import Image

from users.users import Users

from .screen import Screen
from .success import SuccessScreen

from database.storage import get_session
from sqlalchemy.sql import text

from .screen_manager import ScreenManager

from env import monospace

class IDCardScreen(Screen):
    def __init__(self, screen, user, **kwargs):
        super(IDCardScreen, self).__init__(screen)

        self.user = user

        self.objects.append(Button(
            self.screen,
            text = "BACK",
            pos=(30,30),
            font = monospace,
            click=self.back,
            size=30
        ))

        self.objects.append(Label(
            self.screen,
            text = self.user["name"],
            pos=(30, 120),
            size=70
        ))

        self.objects.append(Label(
            self.screen,
            text = "Momentan zugeordnet:",
            pos=(30, 300)
        ))

        self.id_label = Label(
            self.screen,
            text = self.user['id_card'],
            pos=(50, 400),
            size=70
        )
        self.objects.append(self.id_label)

        self.objects.append(Label(
            self.screen,
            text = "Scanne deine ID,",
            pos=(30, 550),
            size=60
        ))
        self.objects.append(Label(
            self.screen,
            text = "um sie zuzuweisen.",
            pos=(30, 600),
            size=60
        ))

        self.objects.append(Button(
            self.screen,
            text='Abbrechen',
            pos=(290, 700),
            size=30,
            click=self.btn_home,
        ))

    def back(self, param, pos):
        screen_manager = ScreenManager.get_instance()
        screen_manager.go_back()

    def home(self):
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()

    def btn_home(self, param, pos):
        self.home()

    def on_barcode(self, barcode):
        if not barcode:
            return
        Users.set_id_card(self.user, barcode)
        self.id_label.text = barcode
