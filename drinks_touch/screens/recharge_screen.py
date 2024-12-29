from functools import partial

import config
from database.models import Account
from elements.button import Button
from elements.hbox import HBox
from elements.image import Image
from elements.label import Label
from elements.vbox import VBox
from users.qr import make_sepa_qr
from .confirm_recharge_screen import ConfirmRechargeScreen
from .screen import Screen


class RechargeScreen(Screen):
    def __init__(self, account: Account):
        super().__init__()
        self.account = account

    def on_start(self, *args, **kwargs):

        qr_file = make_sepa_qr(
            20,
            self.account.name,
            self.account.ldap_id,
            pixel_width=7,
            border=4,
            color="black",
            bg="yellow",
        )
        self.objects = [
            Label(
                text=self.account.name,
                pos=(5, 5),
            ),
            VBox(
                [
                    Label(
                        text="Guthaben",
                        size=20,
                    ),
                    Label(
                        text=f"{self.account.balance} €",
                        size=40,
                    ),
                ],
                pos=(config.SCREEN_WIDTH - 5, 5),
                align_right=True,
            ),
            VBox(
                [
                    Label(text="Wähle den Betrag,", size=30),
                    Label(text="wirf Bargeld in die Kasse:", size=30),
                    HBox(
                        [
                            Button(
                                text="5€",
                                on_click=partial(self.confirm_payment, 5),
                                padding=10,
                            ),
                            Button(
                                text="10€",
                                on_click=partial(self.confirm_payment, 10),
                                padding=10,
                            ),
                            Button(
                                text="20€",
                                on_click=partial(self.confirm_payment, 20),
                                padding=10,
                            ),
                            Button(
                                text="50€",
                                on_click=partial(self.confirm_payment, 50),
                                padding=10,
                            ),
                            Button(
                                text="100€",
                                on_click=partial(self.confirm_payment, 100),
                                padding=10,
                            ),
                        ],
                        gap=15,
                    ),
                    Label(text="Oder überweise per SEPA:", size=30),
                    Image(src=qr_file, size=(300, 330)),
                ],
                pos=(5, 100),
            ),
        ]

    def confirm_payment(self, amount: int):
        confirm_screen = ConfirmRechargeScreen(self.account, amount)
        self.goto(confirm_screen)
