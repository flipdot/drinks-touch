import functools

from sqlalchemy import select

import config
from database.models import Account, Drink
from database.storage import with_db, Session
from screens.add_new_drink import AddNewDrinkScreen
from screens.confirm_payment_screen import ConfirmPaymentScreen
from screens.edit_drink import EditDrinkScreen
from state import GlobalState
from elements import Label, Button, SvgIcon
from elements.hbox import HBox
from elements.spacer import Spacer
from elements.vbox import VBox
from screens.main import MainScreen
from screens.profile import ProfileScreen
from screens.screen import Screen
from screens.search_account import SearchAccountScreen


class DrinkScannedScreen(Screen):

    @with_db
    def __init__(self, barcode: str):
        super().__init__()
        self.barcode = barcode

    @with_db
    def on_start(self, *args, **kwargs):
        query = select(Account).where(Account.id_card == self.barcode)
        account = Session().execute(query).scalar_one_or_none()
        if account:
            self.goto(ProfileScreen(account), replace=True)
            return

        query = select(Drink).where(Drink.ean == self.barcode)
        drink = Session().execute(query).scalar_one_or_none()
        if drink is None:
            if not config.DEFAULT_DRINK_PRICE:
                self.goto(AddNewDrinkScreen(self.barcode), replace=True)
                return
            drink = Drink(
                ean=self.barcode, name="Unbekannt", price=config.DEFAULT_DRINK_PRICE
            )
            Session().add(drink)

        if not drink.price:
            if config.DEFAULT_DRINK_PRICE:
                drink.price = config.DEFAULT_DRINK_PRICE
            else:
                self.goto(EditDrinkScreen(drink), replace=True)
                return

        GlobalState.selected_drink = drink
        if GlobalState.selected_account:
            self.goto(
                ConfirmPaymentScreen(
                    GlobalState.selected_account, GlobalState.selected_drink
                ),
                replace=True,
            )
            return

        self.objects = [
            Label(
                text=drink.name,
                size=40,
                pos=(5, 5),
            ),
            VBox(
                [
                    # Label(
                    #     text=drink.name,
                    #     size=30,
                    # ),
                    # Spacer(height=20),
                    HBox(
                        [
                            Spacer(width=config.SCREEN_WIDTH / 4),
                            Label(
                                text=f"{drink.price:.02f} €",
                                size=70,
                            ),
                        ]
                    ),
                    Spacer(height=10),
                    Label(
                        text=f"EAN: {drink.ean}",
                        size=20,
                    ),
                ],
                pos=(5, 270),
            ),
            HBox(
                [
                    Button(
                        size=45,
                        text=" Buchen ",
                        on_click=lambda: self.goto(MainScreen(), replace=True),
                    ),
                    Button(
                        text=None,
                        inner=SvgIcon(
                            "drinks_touch/resources/images/magnifying-glass.svg",
                            height=53,
                            color=config.Color.PRIMARY,
                        ),
                        on_click=functools.partial(
                            self.goto, SearchAccountScreen(), replace=True
                        ),
                    ),
                ],
                pos=(config.SCREEN_WIDTH - 80, config.SCREEN_HEIGHT - 100),
                align_bottom=True,
                align_right=True,
            ),
        ]

    def on_barcode(self, barcode: str):
        if not barcode:
            self.goto(SearchAccountScreen(), replace=True)
            return
        self.goto(DrinkScannedScreen(barcode), replace=True)
