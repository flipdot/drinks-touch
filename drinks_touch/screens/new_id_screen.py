import subprocess
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from functools import partial
from pystrich.code128 import Code128Encoder

from config import FONTS
from database.models.recharge_event import RechargeEvent
from database.storage import get_session
from elements.button import Button
from elements.label import Label
from elements.progress import Progress
from users.users import Users
from .profile import ProfileScreen
from .screen import Screen
from .screen_manager import ScreenManager


class NewIDScreen(Screen):
    def __init__(self, screen):
        super(NewIDScreen, self).__init__(screen)

        self.objects.append(
            Button(
                self.screen,
                text="BACK",
                pos=(30, 30),
                font=FONTS["monospace"],
                click_func=self.back,
                size=30,
            )
        )

        self.timeout = Progress(
            self.screen,
            pos=(200, 50),
            speed=1 / 30.0,
            on_elapsed=self.time_elapsed,
        )
        self.objects.append(self.timeout)
        self.timeout.start()

        self.objects.append(
            Label(
                self.screen, text="Prepaid Barcode generieren", pos=(30, 120), size=50
            )
        )
        self.objects.append(
            Label(
                self.screen,
                text="Wie viel hast du eingeworfen?",
                pos=(30, 220),
                size=40,
            )
        )
        self.message = Label(self.screen, text="", pos=(50, 320), size=40)
        self.objects.append(self.message)

        for i, euro in enumerate([5, 10, 20, 50]):
            self.objects.append(
                Button(
                    self.screen,
                    text="EUR " + str(euro),
                    pos=((i % 2) * 200 + 30, 600 + (i / 2 * 80)),
                    size=30,
                    click_func=partial(self.btn_euro, euro),
                )
            )

        self.progress = Progress(
            self.screen,
            pos=(200, 420),
            size=100,
            speed=1 / 10.0,
            on_elapsed=self.time_elapsed,
        )
        self.progress.stop()
        self.objects.append(self.progress)

    @staticmethod
    def home():
        from .screen_manager import ScreenManager

        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()

    def time_elapsed(self):
        self.home()

    def btn_euro(self, euro):
        try:
            self.message.text = "Konto wird erzeugt..."
            self.progress.speed = 1 / 20.0
            self.progress.start()
            self.progress.on_elapsed = None
            self.progress.value = 0
            user = Users.create_temp_user()
            print("Created temp %s with EUR %d" % (user["id_card"], euro))
            self.progress.value = 0.2
            self.message.text = "Guthaben wird gespeichert..."
            self.aufladen(user, euro)

            barcode = user["id_card"]

            self.message.text = "ID-Card wird generiert..."
            code_img = self.generate_barcode(barcode)
            self.progress.value = 0.4
            self.message.text = "reticulating splines..."
            receipt_img = self.generate_receipt(euro, code_img)
            self.progress.value = 0.6
            self.message.text = "reloading fobblewobbles..."
            png = self.to_png(receipt_img)
            self.progress.value = 0.8
            self.message.text = "ID-Card wird gedruckt..."
            self.print_png(png)
            self.progress.on_elapsed = self.time_elapsed
            self.progress.stop()
            ScreenManager.get_instance().set_active(ProfileScreen(self.screen, user))
        except Exception as e:
            self.message.text = "Fehler: " + str(e)
            self.progress.value = 0
            self.progress.speed = 1 / 5.0

    @staticmethod
    def aufladen(user, euro):
        session = get_session()
        ev = RechargeEvent(user["id"], user["id"], euro)
        session.add(ev)
        session.commit()

    @staticmethod
    def generate_barcode(barcode):
        enc = Code128Encoder(barcode)
        enc.height = 300
        png = enc.get_imagedata()
        return Image.open(BytesIO(png))

    @staticmethod
    def generate_receipt(euro, code_img):
        # width = 136
        width = 500
        # height = int(width*1.4)
        height = int(width * 1)
        img = Image.new("L", (width, height), "white")
        # code_img = code_img.transpose(Image.ROTATE_90)
        code_img = code_img.resize((int(width * 1.13), int(height * 0.5)), Image.LANZOS)
        # code_img = code_img.resize((int(width * 0.5), int(height * 1.0)), Image.ANTIALIAS)
        # img.paste(code_img, (int(0.4*width), int(0.0*height)))
        img.paste(code_img, (int(-0.07 * width), int(0.2 * height)))

        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(
            font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size=width // 10
        )
        draw.text(
            (int(0.05 * width), int(0.0 * height)),
            "flipdot ID-Card",
            fill="#000",
            font=font,
        )
        draw.text(
            (int(0.05 * width), int(0.1 * height)),
            "Wert: EUR " + str(euro),
            fill="#000",
            font=font,
        )
        return img

    @staticmethod
    def to_png(img):
        img.show()
        img_io = BytesIO()
        img.save(img_io, format="PNG")
        img_data = img_io.getvalue()
        img_io.close()
        return img_data

    @staticmethod
    def print_png(img):
        p = subprocess.Popen(["lp", "-d", "bondrucker", "-"], stdin=subprocess.PIPE)
        p.communicate(input=img)
        # with open("print.png", "w") as f:
        #    f.write(img)
        # print("image written to print.png")
