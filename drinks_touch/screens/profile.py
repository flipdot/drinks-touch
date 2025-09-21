import config
from config import Font
from database.models import Account
from database.storage import with_db
from drinks.drinks_manager import GlobalState
from elements import SvgIcon
from elements.button import Button
from elements.hbox import HBox
from elements.label import Label
from elements.vbox import VBox
from screens.recharge_screen import RechargeScreen
from .confirm_payment_screen import ConfirmPaymentScreen
from .enable_transaction_history_screen import EnableTransactionHistoryScreen
from .id_card_screen import IDCardScreen
from .screen import Screen
from .transaction_history_log_screen import TransactionHistoryLogScreen
from .transfer_balance_screen import TransferBalanceScreen


class ProfileScreen(Screen):
    idle_timeout = 20

    def __init__(self, account: Account):
        super().__init__()

        self.account = account
        self.processing = None
        self.drink_info = None
        self.zuordnen = None
        self.btn_abbrechen = None
        self.elements_aufladungen = []
        self.elements_drinks = []

    @with_db
    def on_start(self, *args, **kwargs):
        if GlobalState.selected_drink:
            self.goto(ConfirmPaymentScreen(self.account, GlobalState.selected_drink))
            return

        button_width = config.SCREEN_WIDTH - 10
        icon_text_gap = 15
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
            VBox(
                [
                    Label(
                        text="Scanne eine",
                        size=50,
                    ),
                    Label(
                        text="Flasche",
                        size=50,
                    ),
                    Label(text="oder wähle:", size=25),
                ],
                pos=(5, 100),
            ),
            VBox(
                [
                    Button(
                        on_click=self.goto_transaction_history,
                        inner=HBox(
                            [
                                SvgIcon(
                                    "drinks_touch/resources/images/clock.svg",
                                    height=40,
                                    color=config.Color.PRIMARY,
                                ),
                                Label(text="Transaktionshistorie"),
                            ],
                            gap=icon_text_gap,
                        ),
                        padding=20,
                        width=button_width,
                    ),
                    Button(
                        on_click=lambda: self.goto(RechargeScreen(self.account)),
                        inner=HBox(
                            [
                                SvgIcon(
                                    "drinks_touch/resources/images/trending-up.svg",
                                    height=40,
                                    color=config.Color.PRIMARY,
                                ),
                                Label(text="Aufladen"),
                            ],
                            gap=icon_text_gap,
                        ),
                        padding=20,
                        width=button_width,
                    ),
                    Button(
                        on_click=lambda: self.goto(TransferBalanceScreen(self.account)),
                        inner=HBox(
                            [
                                SvgIcon(
                                    "drinks_touch/resources/images/repeat.svg",
                                    height=40,
                                    color=config.Color.PRIMARY,
                                ),
                                Label(text="Guthaben übertragen"),
                            ],
                            gap=icon_text_gap,
                        ),
                        padding=20,
                        width=button_width,
                    ),
                    Button(
                        font=Font.MONOSPACE,
                        on_click=lambda: self.goto(IDCardScreen(self.account)),
                        inner=HBox(
                            [
                                SvgIcon(
                                    "drinks_touch/resources/images/link.svg",
                                    height=40,
                                    color=config.Color.PRIMARY,
                                ),
                                Label(text="ID card"),
                            ],
                            gap=icon_text_gap,
                        ),
                        padding=20,
                        width=button_width,
                    ),
                ],
                pos=(5, 300),
                gap=15,
            ),
            # Image(
            #     src="drinks_touch/resources/images/new-text.png",
            #     pos=(330, 370),
            # ),
        ]
        return

    @with_db
    def goto_transaction_history(self):
        if self.account.tx_history_visible:
            self.goto(TransactionHistoryLogScreen(self.account))
        else:
            self.goto(EnableTransactionHistoryScreen(self.account))

    @with_db
    def on_barcode(self, barcode):
        from .drink_scanned import DrinkScannedScreen

        if not barcode:
            return
        self.goto(DrinkScannedScreen(barcode))

    def show_aufladungen(self):
        for d in self.elements_drinks:
            self.objects.remove(d)
        self.objects.extend(self.elements_aufladungen)

    def show_drinks(self):
        for d in self.elements_aufladungen:
            self.objects.remove(d)
        self.objects.extend(self.elements_drinks)
