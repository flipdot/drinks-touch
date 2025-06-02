import datetime

import pygame

import config
from database.models import ScanEvent, Tx
from database.storage import Session
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
                        text=f"EAN: {self.drink['ean']}",
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

    def save_drink(self):
        with Session() as session:
            with session.begin():
                transaction = Tx(
                    payment_reference=f'Kauf "{self.drink["name"]}"',
                    ean=self.drink["ean"],
                    account_id=self.account.id,
                    amount=-1,  # "Alles 1 Euro" policy
                )
                session.add(transaction)
                session.flush()
                ev = ScanEvent(
                    self.drink["ean"],
                    self.account.ldap_id,
                    datetime.datetime.now(),
                    tx_id=transaction.id,
                )
                session.add(ev)
                session.commit()
        DrinksManager.instance.set_selected_drink(None)

        self.goto(
            SuccessScreen(
                self.account,
                self.drink,
                f"getrunken: {self.drink['name']}",
                offer_games=True,
            ),
            replace=True,
        )
