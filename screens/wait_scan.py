# coding=utf-8
import pygame
from env import is_pi

from elements.label import Label
from elements.button import Button
from elements.image import Image

from drinks.drinks import get_by_ean
from drinks.drinks_manager import DrinksManager

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
                pos=(60, 550),
                text="jetzt member zuordnen",
                click=self.set_member
            ),
            Button(
                self.screen,
                pos=(60, 610),
                text="verwerfen",
                click=self.btn_reset
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

        for o in self.scanned_info:
            self.objects.append(o)

        if is_pi():
            self.reset()

    def show_scanned_info(self, show):
        for o in self.scanned_info:
            o.is_visible = show
    
    def on_barcode(self, barcode):
        drink = get_by_ean(barcode)
        DrinksManager.get_instance().set_selected_drink(drink)
        self.barcode_label.text = drink['name']
        self.show_scanned_info(True)

    def set_member(self, args, pos):
        self.reset()
        main = MainScreen(self.screen)
        ScreenManager.get_instance().set_active(main)

    def btn_reset(self, args, pos):
        self.reset()

    def reset(self):
        DrinksManager.get_instance().set_selected_drink(None)
        self.barcode_label.text = None
        self.show_scanned_info(False)

    def back(self, param, pos):
        Users.reset_active()
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()
