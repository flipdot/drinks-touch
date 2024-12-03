import functools

from sqlalchemy import func

from database.models import Account
from database.storage import Session
from elements import SvgIcon
from elements.button import Button
from elements.label import Label
from elements.progress import Progress
from .names import NamesScreen
from .screen import Screen


class MainScreen(Screen):
    def __init__(self):
        super().__init__()
        self.timeout = None

    def on_start(self, *args, **kwargs):
        self.objects = []
        self.objects.append(
            SvgIcon(
                "drinks_touch/resources/images/flipdot.svg",
                width=400,
                pos=(40, 20),
            ),
        )

        self.objects.append(Label(text="member auswählen", pos=(65, 250), size=40))

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
        screen_manager.set_active(NamesScreen(param))

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
        account = Account.query.filter(Account.id_card == barcode).first()
        if account:
            ScreenManager.get_instance().set_active(ProfileScreen(account))

    @staticmethod
    def __get_pos(i):

        row = int(i / 6)
        col = int(i % 6)

        return col * 80 + 5, row * 80 + 350
