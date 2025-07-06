import functools
import math

from sqlalchemy import select

from database.models import Account
from database.storage import Session, with_db
from elements.button import Button
from elements.label import Label
from screens.profile import ProfileScreen
from .screen import Screen


class NamesScreen(Screen):
    def __init__(self, char):
        super().__init__()
        self.char = char
        self.timeout = None

    @with_db
    def on_start(self, *args, **kwargs):
        self.objects = []

        self.objects.append(
            Label(
                text="Wer bist du?",
                pos=(5, 5),
            )
        )

        query = (
            select(Account)
            .filter(Account.name.ilike(self.char + "%"))
            .filter(Account.enabled)
            .order_by(Account.name)
        )
        accounts = Session().execute(query).scalars().all()

        btns_y = 7
        num_cols = int(math.ceil(len(accounts) / float(btns_y)))
        for i, account in enumerate(accounts):
            xoff, yoff = 5, 100
            btn_ypos = 90
            i_y = i % btns_y
            i_x = i // btns_y
            x = i_x * (self.width / num_cols)
            y = i_y * btn_ypos
            self.objects.append(
                Button(
                    text=account.name,
                    pos=(xoff + x, y + yoff),
                    on_click=functools.partial(self.goto, ProfileScreen(account)),
                    padding=20,
                )
            )
            i += 1

    @with_db
    def on_barcode(self, barcode):
        if not barcode:
            return
        query = select(Account).where(Account.id_card == barcode)
        account = Session().execute(query).scalar_one_or_none()
        if account:
            self.goto(ProfileScreen(account))
