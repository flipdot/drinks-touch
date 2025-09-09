from sqlalchemy import select, insert

import config
from database.models import Account, TetrisPlayer
from database.storage import Session, with_db
from elements import SvgIcon, Label, Button
from elements.hbox import HBox
from screens.screen import Screen
from screens.success import TetrisIcon
from screens.tetris.screen import TetrisScreen


class PartyScreen(Screen):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        query = select(Account).filter(Account.name == "recharge")
        self.account = Session().execute(query).scalar_one_or_none()
        if not self.account:
            Session().execute(insert(Account).values(name="recharge"))
            self.account = Session().execute(query).scalar_one()
            Session().execute(
                insert(TetrisPlayer).values(
                    account_id=self.account.id,
                    color="#FF6633",
                )
            )

    @with_db
    def on_start(self, *args, **kwargs):
        self.objects = [
            SvgIcon(
                "drinks_touch/resources/images/mate.svg",
                width=config.SCREEN_WIDTH / 2,
                pos=(config.SCREEN_WIDTH / 4, 20),
                color=config.Color.PRIMARY,
            ),
            SvgIcon(
                "drinks_touch/resources/images/recharge.svg",
                width=400,
                pos=(40, 400),
            ),
            Button(
                inner=HBox(
                    [
                        TetrisIcon(),
                        Label(
                            text="einen Stein setzen",
                            size=30,
                            padding=(5, 10, 0),
                        ),
                    ]
                ),
                on_click=lambda: self.goto(TetrisScreen(self.account)),
                size=20,
                pos=(40, config.SCREEN_HEIGHT - 100),
            ),
        ]

    def on_barcode(self, barcode):
        self.goto(TetrisScreen(self.account))
