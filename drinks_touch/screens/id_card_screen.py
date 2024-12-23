import time

import subprocess
from pystrich.code128 import Code128Encoder

from config import Font
from database.models import Account
from drinks.drinks import get_by_ean
from drinks.drinks_manager import DrinksManager
from elements.button import Button
from elements.label import Label
from .screen import Screen
from .screen_manager import ScreenManager


class IDCardScreen(Screen):
    def __init__(self, account: Account):
        super().__init__()

        self.account = account
        self.timeout = None
        self.id_label = None

    def on_start(self, *args, **kwargs):
        self.objects = []

        self.objects.append(
            Button(
                text="Reset",
                pos=(350, 30),
                size=30,
                on_click=self.reset_id,
            )
        )

        self.objects.append(Label(text=self.account.name, pos=(30, 120), size=70))

        self.objects.append(Label(text="Momentan zugeordnet:", pos=(30, 300)))

        self.id_label = Label(
            text=self.account.id_card,
            pos=(50, 400),
            size=70,
            font=Font.SANS_SERIF,
        )
        self.objects.append(self.id_label)

        self.objects.append(Label(text="Scanne deine ID,", pos=(30, 550), size=60))
        self.objects.append(Label(text="um sie zuzuweisen.", pos=(30, 600), size=60))

        self.objects.append(
            Button(
                text="OK bye",
                pos=(330, 700),
                size=30,
                on_click=self.btn_home,
            )
        )

        self.objects.append(
            Button(
                text="Drucken",
                pos=(30, 700),
                size=30,
                on_click=self.print_id,
            )
        )

    @staticmethod
    def home():
        from .screen_manager import ScreenManager

        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()

    def btn_home(self):
        self.home()

    def set_id(self, ean):
        ean = ean.upper() if ean else ean
        self.id_label.text = self.account.id_card = ean

    def reset_id(self):
        self.set_id(None)

    def print_id(self):
        if not self.account.id_card:
            self.set_id("fd_" + bytes.decode(self.account.name))
        enc = Code128Encoder(str(self.account.id_card))
        enc.height = 300
        png = enc.get_imagedata()
        p = subprocess.Popen(["lp", "-d", "labeldrucker", "-"], stdin=subprocess.PIPE)
        p.communicate(input=png)
        time.sleep(10)

    def on_barcode(self, barcode):
        if not barcode:
            return
        drink = get_by_ean(barcode)
        if drink and ("tags" not in drink or "unknown" not in drink["tags"]):
            from .profile import ProfileScreen

            DrinksManager.get_instance().set_selected_drink(drink)
            ScreenManager.get_instance().set_active(ProfileScreen(self.account))
            return
        self.set_id(barcode)
