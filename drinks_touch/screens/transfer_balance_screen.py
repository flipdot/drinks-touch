import functools
import logging
from decimal import Decimal

from sqlalchemy import func, select

import config
from database.models import Account
from database.storage import Session, with_db
from elements import Label, Button
from elements.input_field import InputField, InputType
from elements.spacer import Spacer
from elements.vbox import VBox
from overlays.keyboard import KeyboardOverlay
from screens.make_transfer_screen import MakeTransferScreen
from screens.screen import Screen
from screens.screen_manager import ScreenManager

logger = logging.getLogger(__name__)


# cache only the last call of the function,
# because it is called in the render() function.
# Still, we want to get fresh results every time the user changes the input.
@functools.lru_cache(maxsize=1)
@with_db
def auto_complete_account_name(text, except_account: str | None = None, limit=10):
    query = (
        select(Account)
        .where(
            Account.name.ilike(f"{text}%"),
            Account.enabled,
            Account.name != except_account,
        )
        .order_by(Account.name)
        .limit(limit + 1)
    )
    accounts = Session().execute(query).scalars().all()
    res = [account.name for account in accounts]
    if len(res) == limit + 1:
        res[-1] = "..."

    if len(res) >= 1:
        n_char = len(text) + 1
        query = (
            Session()
            .query(
                func.upper(func.substr(Account.name, n_char, 1)).label("n_char"),
                func.count(Account.id),
            )
            .filter(Account.name != except_account)
            .filter(Account.name.ilike(f"{text}%"))
            .group_by("n_char")
            .order_by("n_char")
            .all()
        )
        disabled_characters = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for char, _ in query:
            disabled_characters = disabled_characters.replace(char, "")
        KeyboardOverlay.instance.set_keys_disabled(disabled_characters)
    return res


class TransferBalanceScreen(Screen):

    idle_timeout = 60

    def __init__(self, account: Account):
        super().__init__()
        self.account = account
        self.input_field_account_name = None
        self.input_field_amount = None
        self.label_error_message = None

    @with_db
    def on_start(self, *args, **kwargs):
        def focus(obj):
            ScreenManager.instance.active_object = obj

        # The next line is causing a database query. We use the name inside a lambda –
        # if we don't query it now, the access below would fail.
        account_name = self.account.name
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
                        text="An wen möchtest du Guthaben übertragen?",
                        size=20,
                    ),
                    input_field_account_name := InputField(
                        width=config.SCREEN_WIDTH - 10,
                        height=50,
                        auto_complete=lambda text: auto_complete_account_name(
                            text, except_account=account_name
                        ),
                        only_auto_complete=True,
                        on_submit=lambda _: focus(input_field_amount),
                    ),
                    Spacer(height=40),
                    Label(
                        text="Wie viel Euro möchtest du übertragen?",
                        size=20,
                    ),
                    input_field_amount := InputField(
                        input_type=InputType.POSITIVE_NUMBER,
                        max_decimal_places=2,
                        width=config.SCREEN_WIDTH - 10,
                        height=50,
                        on_submit=lambda _: self.submit(),
                    ),
                    Spacer(height=20),
                    label_error_message := Label(
                        text="",
                        size=20,
                        color=config.Color.ERROR,
                    ),
                    Button(
                        text="Übertragen",
                        on_click=self.submit,
                        padding=10,
                    ),
                ],
                pos=(5, 100),
            ),
        ]

        self.input_field_account_name = input_field_account_name
        self.input_field_amount = input_field_amount
        self.label_error_message = label_error_message

        ScreenManager.instance.active_object = input_field_account_name

    @with_db
    def submit(self):
        account_name = self.input_field_account_name.text
        amount = self.input_field_amount.text
        if not account_name:
            self.label_error_message.text = "Bitte gib einen Accountnamen ein."
            return
        if not amount:
            self.label_error_message.text = "Bitte gib einen Betrag ein."
            return

        query = select(Account).where(Account.name == account_name)
        account = Session().execute(query).scalar_one_or_none()
        if not account:
            self.label_error_message.text = "Account nicht gefunden."
            return

        try:
            amount_decimal = Decimal(amount)
        except ValueError as e:
            logger.error(e)
            self.label_error_message.text = str(e)
            return

        if amount_decimal <= 0:
            self.label_error_message.text = "Der Betrag muss größer als 0 sein."
            return

        self.label_error_message.text = ""

        self.goto(MakeTransferScreen(self.account, account, amount_decimal))
