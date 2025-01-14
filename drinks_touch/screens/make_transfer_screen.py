from decimal import Decimal

from database.models import Account
from elements import Label
from screens.screen import Screen


class MakeTransferScreen(Screen):

    nav_bar_visible = False

    def __init__(self, account: Account, to_account: Account, amount: Decimal):
        super().__init__()
        self.account = account

    def on_start(self, *args, **kwargs):
        self.objects = [
            Label(
                text=self.account.name,
                pos=(5, 5),
            ),
            Label(
                text="ÜBERTRAGEN",
                pos=(5, 100),
            ),
        ]
