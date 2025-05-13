import functools


import config
from database.models import Account
from drinks.drinks import get_by_ean
from drinks.drinks_manager import DrinksManager
from elements import Label, Button, SvgIcon
from elements.hbox import HBox
from elements.spacer import Spacer
from elements.vbox import VBox
from screens.main import MainScreen
from screens.profile import ProfileScreen
from screens.screen import Screen
from screens.search_account import SearchAccountScreen


class DrinkScannedScreen(Screen):

    def __init__(self, barcode: str):
        super().__init__()
        account = Account.query.filter(Account.id_card == barcode).first()
        if account:
            self.account = account
            return
        self.account = None
        self.drink = get_by_ean(barcode)
        self.ean = barcode

    def on_start(self, *args, **kwargs):
        if self.account:
            self.goto(ProfileScreen(self.account), replace=True)
            return
        DrinksManager.instance.set_selected_drink(self.drink)
        self.objects = [
            Label(
                text="Getränk gescannt",
                size=40,
                pos=(5, 5),
            ),
            VBox(
                [
                    Label(
                        text=self.drink["name"],
                        size=30,
                    ),
                    Spacer(height=20),
                    Label(
                        text="1,00 €",
                        size=80,
                    ),
                    Spacer(height=10),
                    Label(
                        text=f"EAN: {self.ean}",
                        size=20,
                    ),
                ],
                pos=(5, 250),
            ),
            HBox(
                [
                    Button(
                        size=45,
                        text=" Buchen ",
                        on_click=functools.partial(
                            self.goto, MainScreen(), replace=True
                        ),
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
