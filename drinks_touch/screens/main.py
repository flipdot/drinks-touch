import functools
import random
from datetime import datetime

from sqlalchemy import func, select

from database.models import Account
from database.storage import Session, with_db
from elements import SvgIcon
from elements.button import Button
from elements.label import Label
from .names import NamesScreen
from .screen import Screen


class MainScreen(Screen):
    def __init__(self):
        super().__init__()
        self.timeout = None

    @with_db
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
            select(
                func.upper(func.substr(Account.name, 1, 1)).label("first_char"),
                func.count(Account.id),
            )
            .group_by("first_char")
            .order_by("first_char")
        )

        rows = Session().execute(query).all()

        today = datetime.now().date()
        april_fools = today.month == 4 and today.day == 1

        if april_fools:
            random.shuffle(rows)

        for first_char, count in rows:
            text = first_char
            self.objects.append(
                Button(
                    text=text,
                    pos=self.__get_pos(i),
                    on_click=functools.partial(self.switch_to_screen, text),
                    padding=(15, 25),
                )
            )
            i += 1

    def switch_to_screen(self, param):
        from .screen_manager import ScreenManager

        screen_manager = ScreenManager.instance
        screen_manager.set_active(NamesScreen(param))

    @with_db
    def on_barcode(self, barcode):
        from .screen_manager import ScreenManager
        from .profile import ProfileScreen

        if not barcode:
            return
        query = select(Account).where(Account.id_card == barcode)
        account = Session().execute(query).scalar_one_or_none()
        if account:
            ScreenManager.instance.set_active(ProfileScreen(account))

    @staticmethod
    def __get_pos(i):

        row = int(i / 6)
        col = int(i % 6)

        return col * 80 + 5, row * 80 + 350
