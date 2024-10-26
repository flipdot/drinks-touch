import functools

from sqlalchemy import func

from database.models import Account
from database.storage import Session
from elements.button import Button
from elements.image import Image
from elements.label import Label
from elements.progress import Progress
from users.users import Users
from .names import NamesScreen
from .screen import Screen


class MainScreen(Screen):
    def __init__(self, screen):
        super().__init__(screen)
        self.timeout = None

    def on_start(self, *args, **kwargs):
        self.objects = []
        self.objects.append(Image(pos=(30, 20)))

        self.objects.append(Label(text="member auswählen", pos=(65, 250), size=50))

        i = 0

        query = (
            Session()
            .query(
                func.upper(func.substr(Account.name, 1, 1)).label("first_char"),
                func.count(Account.id),
            )
            .group_by("first_char")
            .order_by("first_char")
            .all()
        )

        for first_char, count in query:
            text = first_char
            self.objects.append(
                Button(
                    text=text,
                    pos=self.__get_pos(i),
                    on_click=functools.partial(self.switch_to_screen, text),
                    force_width=440 / 6,
                    force_height=440 / 6,
                    padding=(15, 25),
                )
            )
            i += 1

        self.objects.append(
            Button(
                text="Abbrechen",
                pos=(150, 700),
                size=30,
                on_click=self.home,
            )
        )
        self.timeout = Progress(
            pos=(380, 715),
            speed=1 / 15.0,
            on_elapsed=self.time_elapsed,
        )
        self.objects.append(self.timeout)
        self.timeout.start()

    def switch_to_screen(self, param):
        from .screen_manager import ScreenManager

        screen_manager = ScreenManager.get_instance()
        screen_manager.set_active(NamesScreen(self.screen, param))

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
            ScreenManager.get_instance().set_active(ProfileScreen(self.screen, user))

    @staticmethod
    def __get_pos(i):

        row = int(i / 6)
        col = int(i % 6)

        return col * 80 + 5, row * 80 + 350
