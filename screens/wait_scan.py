# coding=utf-8
import pygame

from elements.label import Label
from elements.button import Button
from elements.image import Image

from .screen import Screen

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
                text="jetzt member zuordnen"
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

        self.show_scanned_info(False)

    def show_scanned_info(self, show):
        for o in self.scanned_info:
            o.is_visible = show
    
    def on_barcode(self, barcode):
        self.barcode_label.text = barcode
        self.show_scanned_info(True)

    def back(self, param, pos):
        Users.reset_active()
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()
