from elements.button import Button
from elements.image import Image
from elements.label import Label
from elements.progress import Progress
from users.users import Users
from .names import NamesScreen
from .screen import Screen


class MainScreen(Screen):
    def __init__(self, screen):
        super(MainScreen, self).__init__(screen)

        self.objects.append(Image(
            self.screen,
            pos=(30, 20)
        ))

        self.objects.append(Label(
            self.screen,
            text=u'member auswählen',
            pos=(65, 250),
            size=50
        ))

        all_users = list(Users.get_all())
        i = 0

        for c in range(97, 97 + 26):
            text = str(chr(c))
            users = list(filter(lambda u: u["name"].lower().startswith(text), all_users))
            if len(users) == 0:
                continue
            self.objects.append(Button(
                self.screen,
                text=text,
                pos=self.__get_pos(i),
                click_func_param=self.switch_to_screen,
                click_param=text,
                force_width=440 / 6,
                force_height=440 / 6,
            ))

            i += 1

        self.objects.append(Button(
            self.screen,
            text='Abbrechen',
            pos=(150, 700),
            size=30,
            click_func=self.home,
        ))
        self.timeout = Progress(
            self.screen,
            pos=(380, 715),
            speed=1 / 15.0,
            on_elapsed=self.time_elapsed,
        )
        self.objects.append(self.timeout)
        self.timeout.start()

    def switch_to_screen(self, param):
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_active(
            NamesScreen(self.screen, param)
        )

    @staticmethod
    def home():
        from .screen_manager import ScreenManager
        ScreenManager.get_instance().set_default()

    def time_elapsed(self):
        self.home()

    def on_barcode(self, barcode):
        from .screen_manager import ScreenManager
        from .profile import ProfileScreen
        if not barcode:
            return
        user = Users.get_by_id_card(barcode)
        if user:
            ScreenManager.get_instance().set_active(
                ProfileScreen(self.screen, user)
            )

    @staticmethod
    def __get_pos(i):

        row = int(i / 6)
        col = int(i % 6)

        return col * 80 + 30, row * 80 + 350
