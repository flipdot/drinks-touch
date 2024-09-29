import time

import subprocess
from pystrich.code128 import Code128Encoder

from drinks.drinks import get_by_ean
from drinks.drinks_manager import DrinksManager
from elements.button import Button
from elements.label import Label
from elements.progress import Progress
from env import monospace
from users.users import Users
from .screen import Screen
from .screen_manager import ScreenManager


class IDCardScreen(Screen):
    def __init__(self, screen, user):
        super(IDCardScreen, self).__init__(screen)

        self.user = user

        self.objects.append(
            Button(
                self.screen,
                text="BACK",
                pos=(30, 30),
                font=monospace,
                click_func=self.back,
                size=30,
            )
        )

        self.timeout = Progress(
            self.screen,
            pos=(200, 50),
            speed=1 / 15.0,
            on_elapsed=self.time_elapsed,
        )
        self.objects.append(self.timeout)
        self.timeout.start()

        self.objects.append(
            Button(
                self.screen,
                text="Reset",
                pos=(350, 30),
                size=30,
                click_func=self.reset_id,
            )
        )

        self.objects.append(
            Label(self.screen, text=self.user["name"], pos=(30, 120), size=70)
        )

        self.objects.append(
            Label(self.screen, text="Momentan zugeordnet:", pos=(30, 300))
        )

        self.id_label = Label(
            self.screen, text=self.user["id_card"], pos=(50, 400), size=70, font="Serif"
        )
        self.objects.append(self.id_label)

        self.objects.append(
            Label(self.screen, text="Scanne deine ID,", pos=(30, 550), size=60)
        )
        self.objects.append(
            Label(self.screen, text="um sie zuzuweisen.", pos=(30, 600), size=60)
        )

        self.objects.append(
            Button(
                self.screen,
                text="OK bye",
                pos=(330, 700),
                size=30,
                click_func=self.btn_home,
            )
        )

        self.objects.append(
            Button(
                self.screen,
                text="Drucken",
                pos=(30, 700),
                size=30,
                click_func=self.print_id,
            )
        )
        self.progress = Progress(self.screen, pos=(200, 720), speed=1 / 15.0)
        self.progress.stop()
        self.objects.append(self.progress)

    @staticmethod
    def back():
        screen_manager = ScreenManager.get_instance()
        screen_manager.go_back()

    @staticmethod
    def home():
        from .screen_manager import ScreenManager

        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()

    def time_elapsed(self):
        self.home()

    def btn_home(self):
        self.home()

    def set_id(self, ean):
        ean = ean.upper() if ean else ean
        self.user["id_card"] = ean
        Users.set_value(self.user, "id_card", ean)
        self.id_label.text = self.user["id_card"]

    def reset_id(self):
        self.set_id(None)

    def print_id(self):
        self.progress.start()
        if not self.user["id_card"]:
            self.set_id("fd_" + bytes.decode(self.user["name"]))
        enc = Code128Encoder(str(self.user["id_card"]))
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
            ScreenManager.get_instance().set_active(
                ProfileScreen(self.screen, self.user)
            )
            return
        self.set_id(barcode)
