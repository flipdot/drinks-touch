import config
from database.models import RechargeEvent
from database.storage import get_session
from elements import Label, Button
from elements.hbox import HBox
from elements.vbox import VBox
from screens.screen import Screen
from screens.success import SuccessScreen


class ConfirmRechargeScreen(Screen):

    def __init__(self, account, amount: int):
        super().__init__()
        self.account = account
        self.amount = amount

    def on_start(self):
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
                    Label(text="Hast du", size=35),
                    Label(text=f"{self.amount} €", pos=(30, 200), size=50),
                    Label(text="in die Kasse geworfen?", size=35),
                ],
                pos=(5, 150),
            ),
            HBox(
                [
                    Button(
                        text="Betrag ändern",
                        size=30,
                        on_click=self.back,
                        padding=20,
                    ),
                    Button(
                        text="Ja",
                        size=30,
                        on_click=self.save_payment,
                        padding=20,
                    ),
                ],
                pos=(50, 400),
                gap=15,
            ),
        ]

    def save_payment(self):
        session = get_session()
        ev = RechargeEvent(self.account.ldap_id, "DISPLAY", self.amount)
        session.add(ev)
        session.commit()

        # TODO: replace instead of adding to history
        self.goto(
            SuccessScreen(
                self.account,
                None,
                f"{self.amount} € aufgeladen",
            )
        )
