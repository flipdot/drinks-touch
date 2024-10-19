from config import FONTS
from elements.button import Button
from elements.label import Label
from elements.progress import Progress
from screens.profile import ProfileScreen
from .screen import Screen


class EnterPinScreen(Screen):
    def __init__(self, screen, user):
        super(EnterPinScreen, self).__init__(screen)
        self.user = user

        self.objects.append(
            Button(
                text="BACK",
                pos=(30, 30),
                click_func=self.back,
                font=FONTS["monospace"],
                size=30,
            )
        )

        self.timeout = Progress(
            pos=(200, 50),
            speed=1 / 15.0,
            on_elapsed=self.time_elapsed,
        )
        self.objects.append(self.timeout)
        self.timeout.start()

        self.objects.append(
            Button(
                text="UNLOCK!",
                pos=(100, 680),
                click_func=self.btn_ok,
                font=FONTS["monospace"],
                size=70,
            )
        )

        self.objects.append(
            Label(
                text="/s Barcode oder /e PIN:",
                pos=(40, 110),
            )
        )

        self.input = Label(
            text="_",
            pos=(100, 180),
        )
        self.objects.append(self.input)

        keys = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["#", "0", "*"]]

        x = 0
        y = 0
        for row in keys:
            for label in row:
                self.render_digit_btn(label, x, y)
                x += 1
            x = 0
            y += 1

        self.objects.append(
            Button(
                text="DEL",
                pos=(200, 580),
                font=FONTS["monospace"],
                click_func=self.del_char,
                size=50,
            )
        )

    def render_digit_btn(self, label, x, y):
        width = 480 / 6
        cord_x = width * 1.8 + x * width
        cord_y = 250 + y * width
        self.objects.append(
            Button(
                text=label,
                pos=(cord_x, cord_y),
                click_func_param=self.add_char,
                click_param=label,
                font=FONTS["monospace"],
                size=50,
                force_width=width,
                force_height=width,
            )
        )

    def add_char(self, param):
        self.input.text = self.input.text.split("_")[0] + param
        self.input.text += "_"

    def del_char(self):
        self.input.text = self.input.text[: len(self.input.text) - 2]
        self.input.text += "_"

    def btn_ok(self):
        # TODO check the pin using
        # self.get_pin() and self.user

        from .screen_manager import ScreenManager

        ScreenManager.get_instance().set_active(ProfileScreen(self.screen, self.user))

    def get_pin(self):
        return self.input.text[: len(self.input.text) - 1]

    def switch_to_screen(self, param):
        from .screen_manager import ScreenManager

        screen_manager = ScreenManager.get_instance()
        screen_manager.set_active(ProfileScreen(self.screen, param))

    def on_barcode(self, barcode):
        for c in barcode:
            self.add_char(c)

    @staticmethod
    def home():
        from .screen_manager import ScreenManager

        ScreenManager.get_instance().set_default()

    def time_elapsed(self):
        self.home()
