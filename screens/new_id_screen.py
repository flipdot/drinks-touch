# coding=utf-8
import pygame
import datetime
import subprocess
import time

from elements.label import Label
from elements.button import Button
from elements.image import Image
from elements.progress import Progress

from users.users import Users

from drinks.drinks import get_by_ean
from drinks.drinks_manager import DrinksManager

from .screen import Screen
from .success import SuccessScreen

from database.storage import get_session
from sqlalchemy.sql import text
from database.models.recharge_event import RechargeEvent

from .screen_manager import ScreenManager

from env import monospace
from functools import partial

from hubarcode.code128 import Code128Encoder
from PIL import Image, ImageDraw, ImageFont
from StringIO import StringIO

class NewIDScreen(Screen):
    def __init__(self, screen, **kwargs):
        super(NewIDScreen, self).__init__(screen)

        self.objects.append(Button(
            self.screen,
            text = "BACK",
            pos=(30,30),
            font = monospace,
            click=self.back,
            size=30
        ))

        self.timeout = Progress(
            self.screen,
            pos=(200, 50),
            speed=1/30.0,
            on_elapsed=self.time_elapsed,
        )
        self.objects.append(self.timeout)
        self.timeout.start()

        self.objects.append(Label(
            self.screen,
            text = "Wirf EURO in die Kasse!",
            pos=(30, 120),
            size=50
        ))
        self.objects.append(Label(
            self.screen,
            text = "wieviel hast du reingeworfen?",
            pos=(30, 220),
            size=40
        ))
        self.message = Label(
            self.screen,
            text = "",
            pos=(50, 320),
            size=40
        )
        self.objects.append(self.message)

        for i, euro in enumerate([5,10,20,50]):
            self.objects.append(Button(
                self.screen,
                text="EUR " + str(euro),
                pos=( (i%2)*200 + 30, 600 + (i/2 * 80)),
                size=30,
                click=partial(self.btn_euro, euro)
            ))

        self.progress = Progress(
            self.screen,
            pos=(200,420),
            size=100,
            speed=1/10.0,
            on_elapsed=self.time_elapsed
        )
        self.progress.stop()
        self.objects.append(self.progress)

    def back(self, param, pos):
        screen_manager = ScreenManager.get_instance()
        screen_manager.go_back()

    def home(self):
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()

    def time_elapsed(self):
        self.home()

    def btn_euro(self, euro, param, pos):
        self.message.text = "Konto wird erzeugt..."
        self.progress.speed = 0
        self.progress.start()
        self.progress.value = 0
        user = Users.create_temp_user()
        self.progress.value = 0.2
        self.message.text = "Guthaben wird gespeichert..."
        self.aufladen(user, euro)

        barcode = user['id_card']
        #barcode = "EFDT31456"

        if barcode.startswith("E"):
            barcode = barcode[1:]
        
        self.message.text = "ID-Card wird gedruckt..."
        code_img = self.generate_barcode(euro, barcode)
        self.progress.value = 0.4
        receipt_img = self.generate_receipt(euro, code_img)
        self.progress.value = 0.5
        png = self.to_png(receipt_img)
        self.progress.value = 0.6
        
        self.print_png(png)
        self.progress.value = 0.7
        self.progress.speed = 1/10.0
        time.sleep(self.progress.value / self.progress.speed)

    def aufladen(self, user, euro):
        session = get_session()
        ev = RechargeEvent(
            user["id"],
            user["id"],
            euro
        )
        session.add(ev)
        session.commit()

    def generate_barcode(self, euro, barcode):
        enc = Code128Encoder(barcode)
        enc.height = 300
        png = enc.get_imagedata()
        return Image.open(StringIO(png))
    
    def generate_receipt(self, euro, code_img):
        #width = 136
        width = 500
        #height = int(width*1.4)
        height = int(width*1)
        img = Image.new("L", (width, height), "white")
        #code_img = code_img.transpose(Image.ROTATE_90)
        code_img = code_img.resize((int(width * 1.13), int(height * 0.5)), Image.ANTIALIAS)
        #code_img = code_img.resize((int(width * 0.5), int(height * 1.0)), Image.ANTIALIAS)
        #img.paste(code_img, (int(0.4*width), int(0.0*height)))
        img.paste(code_img, (int(-0.07*width), int(0.2*height)))

        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(font="DejaVuSans.ttf", size=width/10)
        draw.text((int(0.05*width), int(0.0*height)),
            "flipdot ID-Card", fill="#000", font=font)
        draw.text((int(0.05*width), int(0.1*height)),
            "Wert: EUR " + str(euro), fill="#000", font=font)
        return img
    
    def to_png(self, img):
        img.show()
        imgIO = StringIO()
        img.save(imgIO, format="PNG")
        img_data = imgIO.getvalue()
        imgIO.close()
        return img_data
    
    def print_png(self, img):
        p = subprocess.Popen(['lp', '-d', 'bondrucker', '-'], stdin=subprocess.PIPE)
        p.communicate(input=img)
        with open("print.png", "w") as f:
            f.write(img)
        print "image written to print.png"
