import functools

from sqlalchemy import select

import config
from database.models import Account
from database.storage import with_db, Session
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
        self.barcode = barcode
        self.drink = get_by_ean(barcode)
        self.ean = barcode

    @with_db
    def on_start(self, *args, **kwargs):
        query = select(Account).where(Account.id_card == self.barcode)
        account = Session().execute(query).scalar_one_or_none()
        if account:
            self.goto(ProfileScreen(account), replace=True)
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
                        text="Preis: 1 €",
                        size=50,
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
