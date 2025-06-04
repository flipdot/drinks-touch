import functools
import math

from database.models import Account
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
        accounts = (
            Account.query.filter(Account.name.ilike(self.char + "%"))
            .filter(Account.enabled)
            .order_by(Account.name)
            .all()
        )

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
        account = Account.query.filter(Account.id_card == barcode).first()
        if account:
            self.goto(ProfileScreen(account))
