import functools
import logging

import config
from database.models import Account
from elements import Label
from elements.input_field import InputField, InputType
from elements.spacer import Spacer
from elements.vbox import VBox
from screens.screen import Screen
from screens.screen_manager import ScreenManager

logger = logging.getLogger(__name__)


# cache only the last call of the function,
# because it is called in the render() function.
# Still, we want to get fresh results every time the user changes the input.
@functools.lru_cache(maxsize=1)
def auto_complete_account_name(text, except_account: str, limit=10):
    accounts = (
        Account.query.filter(Account.name.ilike(f"{text}%"))
        .filter(Account.name != except_account)
        .order_by(Account.name)
        .limit(limit + 1)
    )
    res = [account.name for account in accounts]
    if len(res) == limit + 1:
        res[-1] = "..."
    return res


class TransferBalanceScreen(Screen):

    idle_timeout = 60

    def __init__(self, account):
        super().__init__()
        self.account = account

    def on_start(self, *args, **kwargs):
        def focus(obj):
            ScreenManager.instance.active_object = obj

        self.objects = [
            Label(
                text=self.account.name,
                pos=(5, 5),
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
                            text, except_account=self.account.name
                        ),
                        only_auto_complete=True,
                        on_complete=lambda _: focus(input_field_amount),
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
                    ),
                    Spacer(height=20),
                    Label(
                        text="Work in progress. Es fehlt:",
                        size=15,
                    ),
                    Label(
                        text="- Nächster Screen zum bestätigen",
                        size=15,
                    ),
                ],
                pos=(5, 100),
            ),
        ]

        ScreenManager.instance.active_object = input_field_account_name
