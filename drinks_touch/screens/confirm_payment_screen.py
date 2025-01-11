import datetime

import config
from database.models import ScanEvent
from database.storage import get_session
from drinks.drinks_manager import DrinksManager
from elements import Label, Button
from elements.vbox import VBox
from screens.screen import Screen
from screens.success import SuccessScreen


class ConfirmPaymentScreen(Screen):

    def __init__(self, account, drink):
        super().__init__()
        self.account = account
        self.drink = drink

    def btn_confirm(self):
        self.account.balance -= self.drink["price"]
        self.goto(
            SuccessScreen(
                self.account,
                self.drink,
                f"getrunken: {self.drink['name']}",
            )
        )

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
            Label(
                text="Auswahl bestätigen",
                pos=(5, 100),
                size=48,
            ),
            VBox(
                [
                    Label(
                        text=f"Getränk: {self.drink['name']}",
                    ),
                    Label(
                        text="Preis: 1 €",
                    ),
                    Label(
                        text=f"EAN: {self.drink['ean']}",
                        size=20,
                    ),
                    # Label(
                    #     text=str(self.drink),
                    #     size=10,
                    # ),
                ],
                gap=15,
                pos=(5, 200),
            ),
            Button(
                text="Trinken",
                on_click=self.save_drink,
                size=60,
                padding=20,
                pos=(100, config.SCREEN_HEIGHT - 100),
                align_bottom=True,
            ),
        ]

    def on_stop(self, *args, **kwargs):
        DrinksManager.instance.set_selected_drink(None)

    def save_drink(self):
        session = get_session()
        ev = ScanEvent(self.drink["ean"], self.account.ldap_id, datetime.datetime.now())
        session.add(ev)
        session.commit()
        DrinksManager.instance.set_selected_drink(None)
        # Legacy: Delete a temp ldap user. They were only used for
        # Gutscheincodes
        # Users.delete_if_nomoney(
        #     {
        #         "path": self.account.ldap_path,
        #         "id": self.account.ldap_id,
        #     }
        # )

        self.goto(
            SuccessScreen(
                self.account,
                self.drink,
                f"getrunken: {self.drink['name']}",
            ),
            replace=True,
        )
