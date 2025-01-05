import functools
import logging

import config
from database.models import Account
from elements import Label
from elements.input_field import InputField, InputType
from elements.spacer import Spacer
from elements.vbox import VBox
from screens.screen import Screen


logger = logging.getLogger(__name__)


# cache only the last call of the function,
# because it is called in the render() function.
# Still, we want to get fresh results every time the user changes the input.
@functools.lru_cache(maxsize=1)
def auto_complete_account_name(text, except_account: str):
    accounts = (
        Account.query.filter(Account.name.ilike(f"{text}%"))
        .filter(Account.name != except_account)
        .order_by(Account.name)
        .limit(5)
    )
    return [account.name for account in accounts]


class TransferBalanceScreen(Screen):

    idle_timeout = 60

    def __init__(self, account):
        super().__init__()
        self.account = account

    def on_start(self, *args, **kwargs):
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
                    InputField(
                        width=config.SCREEN_WIDTH - 10,
                        height=50,
                        auto_complete=lambda text: auto_complete_account_name(
                            text, except_account=self.account.name
                        ),
                        only_auto_complete=True,
                    ),
                    Spacer(height=40),
                    Label(
                        text="Wie viel Euro möchtest du übertragen?",
                        size=20,
                    ),
                    InputField(
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
                        text="- On-Screen-Keyboard",
                        size=15,
                    ),
                    Label(
                        text="    Theoretisch kannst du eine Tastatur anschließen :)",
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
