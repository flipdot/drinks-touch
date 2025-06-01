import functools
import math

from sqlalchemy import select

from database.models import Account
from database.storage import Session
from elements.button import Button
from elements.label import Label
from screens.profile import ProfileScreen
from .screen import Screen


class NamesScreen(Screen):
    def __init__(self, char):
        super().__init__()
        self.char = char
        self.timeout = None

    def on_start(self, *args, **kwargs):
        self.objects = []

        self.objects.append(
            Label(
                text="Wer bist du?",
                pos=(5, 5),
            )
        )

        # users = list(Users.get_all(filters=["uid=" + self.char + "*"]))
        query = (
            select(Account)
            .where(
                Account.name.ilike(self.char + "%"),
                Account.enabled.is_(True),
            )
            .order_by(Account.name)
        )
        with Session() as session:
            accounts = session.scalars(query).all()

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

    def on_barcode(self, barcode):
        if not barcode:
            return
        with Session() as session:
            account = session.scalars(
                select(Account).where(Account.id_card == barcode)
            ).one_or_none()
        if account:
            self.goto(ProfileScreen(account))
