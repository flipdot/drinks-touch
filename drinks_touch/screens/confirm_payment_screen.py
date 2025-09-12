from decimal import Decimal

import pygame

import config
from database.models import Tx, Sale
from database.storage import Session, with_db
from drinks.drinks_manager import DrinksManager
from elements import Label, Button
from elements.base_elm import BaseElm
from elements.spacer import Spacer
from elements.vbox import VBox
from screens.screen import Screen
from screens.success import SuccessScreen


class ConfirmPaymentScreen(Screen):

    def __init__(self, account, drink):
        super().__init__()
        self.account = account
        self.drink = drink

    @with_db
    def on_start(self):
        DrinksManager.instance.set_selected_drink(self.drink)
        price = self.drink.price or Decimal("1.00")
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
                        text=f"Preis: {price:.03} €",
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

    def event(self, event) -> BaseElm | None:
        if event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
            self.save_drink()
        else:
            return super().event(event)

    def on_stop(self, *args, **kwargs):
        DrinksManager.instance.set_selected_drink(None)

    @with_db
    def save_drink(self):
        transaction = Tx(
            payment_reference=f'Kauf "{self.drink.name}"',
            ean=self.drink.ean,
            account_id=self.account.id,
            amount=-1 * (self.drink.price or Decimal("1.00")),
        )
        Session().add(transaction)
        sale = Sale(ean=self.drink.ean)
        Session().add(sale)
        DrinksManager.instance.set_selected_drink(None)

        self.goto(
            SuccessScreen(
                self.account,
                self.drink,
                f"getrunken: {self.drink.name}",
                offer_games=True,
            ),
            replace=True,
        )
