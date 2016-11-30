# coding=utf-8
import pygame
from env import is_pi

from elements.label import Label
from elements.button import Button
from elements.image import Image
from elements.progress import Progress

from users.users import Users

from drinks.drinks import get_by_ean
from drinks.drinks_manager import DrinksManager

from screens.profile import ProfileScreen

from .screen import Screen
from .main import MainScreen
from .screen_manager import ScreenManager

class WaitScanScreen(Screen):
    def __init__(self, screen, **kwargs):
        super(WaitScanScreen, self).__init__(screen)

        self.barcode_label = Label(
            self.screen,
            pos=(60, 400),
        )

        self.scanned_info = [
            self.barcode_label,
            Button(
                self.screen,
                pos=(60, 600),
                text="drink buchen",
                size=60,
                click=self.set_member
            ),
            Button(
                self.screen,
                pos=(270, 700),
                text="verwerfen",
                click=self.btn_reset
            )
        ]
        self.empty_info = [
            Button(
                self.screen,
                pos=(60, 700),
                text="Benutzer",
                click=self.set_member
            )
        ]

        self.objects.append(Image(
            self.screen,
            pos=(30, 20)
        ))

        self.objects.append(Label(
            self.screen,
            text = u"Scanne dein Getränk :)",
            pos=(60, 240),
        ))

        self.progress = Progress(
            self.screen,
            pos=(400, 500),
            size=100,
            speed=3,
            on_elapsed=self.time_elapsed,
        )
        self.objects.append(self.progress)

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
        user = Users.get_by_id_card(barcode)
        if user:
            ScreenManager.get_instance().set_active(
                ProfileScreen(self.screen, user)
            )
            return
        drink = get_by_ean(barcode)
        DrinksManager.get_instance().set_selected_drink(drink)
        self.barcode_label.text = drink['name']
        self.show_scanned_info(True)
        self.progress.start()       

    def set_member(self, args, pos):
        self.reset(False)
        main = MainScreen(self.screen)
        ScreenManager.get_instance().set_active(main)

    def btn_reset(self, args, pos):
        self.reset()

    def reset(self, reset_drink=True):
        if reset_drink:
            DrinksManager.get_instance().set_selected_drink(None)
            self.progress.stop()

        self.barcode_label.text = None
        self.show_scanned_info(False)

    def back(self, param, pos):
        Users.reset_active()
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()
