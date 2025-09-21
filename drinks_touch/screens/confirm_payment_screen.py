import config
from database.models import Tx, Sale, Account, Drink
from database.storage import Session, with_db
from elements import Label, Button
from elements.spacer import Spacer
from elements.vbox import VBox
from notifications.notification import send_drink
from screens.screen import Screen
from screens.success import SuccessScreen


class ConfirmPaymentScreen(Screen):

    def __init__(self, account: Account, drink: Drink):
        super().__init__()
        self.account = account
        self.drink = drink

    @with_db
    def on_start(self):

        if not self.drink.price:
            if config.DEFAULT_DRINK_PRICE:
                self.drink.price = config.DEFAULT_DRINK_PRICE
            else:
                raise NotImplementedError(
                    "Display that a price has yet to be determined"
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
            Label(
                text="Auswahl bestätigen",
                pos=(5, 100),
                size=48,
            ),
            VBox(
                [
                    Label(
                        text=self.drink.name,
                        size=30,
                    ),
                    Spacer(height=20),
                    Label(
                        text=f"Preis: {self.drink.price:.02f} €",
                        size=50,
                    ),
                    Spacer(height=10),
                    Label(
                        text=f"EAN: {self.drink.ean}",
                        size=20,
                    ),
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

    def on_barcode(self, barcode: str):
        if not barcode:
            self.save_drink()
            return

    @with_db
    def save_drink(self):
        assert self.price, "Price must be set before saving a drink"
        transaction = Tx(
            payment_reference=f'Kauf "{self.drink_name}"',
            ean=self.barcode,
            account_id=self.account.id,
            amount=-1 * self.price,
        )
        Session().add(transaction)
        sale = Sale(ean=self.barcode)
        Session().add(sale)

        self.goto(
            SuccessScreen(
                self.account,
                f"getrunken: {self.drink_name}",
                on_start_fn=lambda: send_drink(self.account, self.drink_name),
                offer_games=True,
            ),
            replace=True,
        )
