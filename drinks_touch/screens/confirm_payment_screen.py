import config
from database.models import Tx, Sale, Account, Drink
from database.storage import Session, with_db
from elements import Label, Button
from elements.hbox import HBox
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
                pos=(5, 120),
                size=32,
            ),
            VBox(
                [
                    Label(
                        text=self.drink.name,
                        size=30,
                    ),
                    Spacer(height=20),
                    HBox(
                        [
                            Spacer(width=config.SCREEN_WIDTH / 4),
                            Label(
                                text=f"{self.drink.price:.02f} €",
                                size=70,
                            ),
                        ]
                    ),
                    Spacer(height=10),
                    Label(
                        text=f"EAN: {self.drink.ean}",
                        size=20,
                    ),
                ],
                pos=(5, 250),
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
        from screens.drink_scanned import DrinkScannedScreen

        if not barcode:
            self.save_drink()
            return
        self.goto(DrinkScannedScreen(barcode), replace=True)

    @with_db
    def save_drink(self):
        assert self.drink.price, "Price must be set before saving a drink"
        transaction = Tx(
            payment_reference=f'Kauf "{self.drink.name}"',
            ean=self.drink.ean,
            account_id=self.account.id,
            amount=-1 * self.drink.price,
        )
        Session().add(transaction)
        sale = Sale(ean=self.drink.ean)
        Session().add(sale)

        self.goto(
            SuccessScreen(
                self.account,
                f"getrunken: {self.drink.name}",
                on_start_fn=lambda: send_drink(self.account, self.drink.name),
                offer_games=True,
            ),
            replace=True,
        )

    # @staticmethod
    # def back():
    #     GlobalState.reset()
    #     super(ConfirmPaymentScreen, ConfirmPaymentScreen).back()
