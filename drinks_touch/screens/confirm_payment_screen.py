import config
from database.models import Tx, Sale, Account, Drink
from database.storage import Session, with_db
from drinks.drinks_manager import DrinksManager
from elements import Label, Button
from elements.spacer import Spacer
from elements.vbox import VBox
from notifications.notification import send_drink
from screens.screen import Screen
from screens.success import SuccessScreen


class ConfirmPaymentScreen(Screen):

    def __init__(self, account: Account, barcode: str | None):
        super().__init__()
        self.account = account
        self.barcode = barcode
        self.drink: Drink | None = None

        # Keeping name and price as separate attributes, to allow
        # drinking unknown drinks.
        # Will be refactored later to allow users to create new drink entries in the DB
        self.drink_name = "Unbekannt"
        self.price = config.DEFAULT_DRINK_PRICE

    @with_db
    def on_start(self):
        self.drink = (
            Session().query(Drink).filter(Drink.ean == self.barcode).one_or_none()
        )

        if self.drink:
            self.drink_name = self.drink.name
            self.price = self.drink.price or config.DEFAULT_DRINK_PRICE

        if not self.price:
            raise NotImplementedError("Display that a price has yet to be determined")

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
                        text=self.drink_name,
                        size=30,
                    ),
                    Spacer(height=20),
                    Label(
                        text=f"Preis: {self.price:.02f} €",
                        size=50,
                    ),
                    Spacer(height=10),
                    Label(
                        text=f"EAN: {self.barcode}",
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

    def on_stop(self, *args, **kwargs):
        DrinksManager.instance.selected_barcode = None

    def on_barcode(self, barcode: str):
        if not barcode:
            self.save_drink()
            return
        # DrinksManager.instance.selected_barcode = barcode
        # self.goto(ConfirmPaymentScreen(self.account, barcode), replace=True)

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
