from sqlalchemy import select, func

import config
from config import Color
from database.models import Account, Tx
from database.storage import with_db, Session
from elements import Label, Button, SvgIcon
from elements.hbox import HBox
from elements.vbox import VBox
from screens.screen import Screen
from screens.transaction_history_stats_screen import TransactionHistoryStatsScreen


class TransactionHistoryLogScreen(Screen):
    PAGE_SIZE = 8

    def __init__(self, account: Account):
        super().__init__()

        self.account = account
        self.page = 1
        self.total_pages = 1

    def calculate_hash(self):
        return hash(
            (
                super().calculate_hash(),
                self.page,
                self.total_pages,
            )
        )

    @with_db
    def on_start(self, *args, **kwargs):
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
            HBox(
                [
                    Button(
                        inner=SvgIcon(
                            "drinks_touch/resources/images/trash-2.svg",
                            color=Color.PRIMARY,
                            width=36,
                        ),
                        on_click=lambda: self.alert("Nicht implementiert"),
                    ),
                    Button(
                        inner=SvgIcon(
                            "drinks_touch/resources/images/bar-chart-2.svg",
                            color=Color.PRIMARY,
                            width=36,
                        ),
                        on_click=lambda: self.goto(
                            TransactionHistoryStatsScreen(self.account)
                        ),
                    ),
                    Button(
                        inner=SvgIcon(
                            "drinks_touch/resources/images/lock.svg",
                            color=Color.PRIMARY,
                            width=36,
                        ),
                        on_click=self.toggle_history_lock,
                        pass_on_click_kwargs=True,
                    ),
                ],
                pos=(config.SCREEN_WIDTH - 5, config.SCREEN_HEIGHT - 130),
                gap=15,
                align_right=True,
            ),
            VBox(
                [
                    HBox(
                        [
                            Label(
                                text="Datum",
                                size=24,
                                width=100,
                                color=Color.PRIMARY_DARK,
                            ),
                            Label(
                                text="Referenz",
                                size=24,
                                width=280,
                                color=Color.PRIMARY_DARK,
                            ),
                            Label(
                                text="Betrag",
                                size=24,
                                width=160,
                                color=Color.PRIMARY_DARK,
                            ),
                        ]
                    ),
                    HBox(
                        width=config.SCREEN_WIDTH - 10,
                        height=1,
                        bg_color=Color.PRIMARY_DARK,
                    ),
                ],
                pos=(5, 90),
            ),
        ]
        self.total_items = self.count_transactions()
        self.total_pages = self.total_items // TransactionHistoryLogScreen.PAGE_SIZE + (
            1 if self.total_items % TransactionHistoryLogScreen.PAGE_SIZE > 0 else 0
        )
        self.go_to_page(self.page)

    @with_db
    def load_transactions(self, page: int) -> list[Tx]:
        if not self.account.tx_history_visible:
            return []
        query = (
            select(Tx)
            .where(Tx.account_id == self.account.id)
            .order_by(Tx.created_at.desc())
            .offset((page - 1) * TransactionHistoryLogScreen.PAGE_SIZE)
            .limit(TransactionHistoryLogScreen.PAGE_SIZE)
        )
        return Session().execute(query).scalars().all()

    @with_db
    def count_transactions(self) -> int:
        query = select(func.count(Tx.id)).where(Tx.account_id == self.account.id)
        return Session().execute(query).scalar()

    @with_db
    def toggle_history_lock(self, button: Button):
        self.account.tx_history_visible = not self.account.tx_history_visible
        if self.account.tx_history_visible:
            button.inner.path = "drinks_touch/resources/images/lock.svg"
        else:
            button.inner.path = "drinks_touch/resources/images/unlock.svg"
        self.go_to_page(1)

    @with_db
    def go_to_page(self, page: int):
        if page < 1 or page > self.total_pages:
            return
        self.page = page
        transactions = self.load_transactions(page)
        pagination_text = f"{self.page:4} / {self.total_pages:4}"
        # from_item = (self.page - 1) * TransactionHistoryLogScreen.PAGE_SIZE + 1
        # to_item = min(self.page * TransactionHistoryLogScreen.PAGE_SIZE, self.total_items)
        # pagination_text = f"{from_item:4} - {to_item:4}"
        self.objects = [
            *self.objects[:4],
            VBox(
                [
                    HBox(
                        [
                            VBox(
                                [
                                    Label(
                                        text=tx.created_at.strftime("%Y-%m-%d"),
                                        height=20,
                                        size=15,
                                    ),
                                    Label(
                                        text=tx.created_at.strftime("%H:%M"),
                                        height=20,
                                        size=15,
                                        color=Color.PRIMARY_DARK,
                                    ),
                                ],
                                width=100,
                            ),
                            Label(text=tx.payment_reference, width=245, size=22),
                            Label(
                                text=f"{tx.amount:+7.2f} €",
                                size=22,
                                width=160,
                                height=35,
                                font=config.Font.MONOSPACE,
                                color=Color.GREEN if tx.amount >= 0 else Color.RED,
                            ),
                        ],
                    )
                    for tx in transactions
                ],
                pos=(5, 130),
                gap=15,
            ),
            HBox(
                [
                    Button(text=" « ", on_click=lambda: self.go_to_page(1)),
                    Button(text=" ‹ ", on_click=lambda: self.go_to_page(self.page - 1)),
                    Label(
                        text=pagination_text,
                        size=14,
                        padding=(15, 0),
                        width=110,
                        font=config.Font.MONOSPACE,
                    ),
                    Button(text=" › ", on_click=lambda: self.go_to_page(self.page + 1)),
                    Button(
                        text=" » ", on_click=lambda: self.go_to_page(self.total_pages)
                    ),
                ],
                pos=(10, config.SCREEN_HEIGHT - 255),
                gap=15,
            ),
        ]
