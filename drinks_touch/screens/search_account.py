from sqlalchemy import select

import config
from database.models import Account
from database.storage import Session, with_db
from elements import Label
from elements.input_field import InputField
from screens.profile import ProfileScreen
from screens.screen import Screen
from screens.screen_manager import ScreenManager
from screens.transfer_balance_screen import auto_complete_account_name


class SearchAccountScreen(Screen):

    idle_timeout = 30

    def on_start(self, *args, **kwargs):
        self.objects = [
            Label(
                text="Account suchen",
                size=40,
                pos=(5, 5),
            ),
            (
                input_field_account_name := InputField(
                    pos=(5, 100),
                    on_submit=self.select_account,
                    width=(config.SCREEN_WIDTH - 10),
                    height=80,
                    auto_complete=auto_complete_account_name,
                    only_auto_complete=True,
                )
            ),
        ]
        ScreenManager.instance.active_object = input_field_account_name

    def tick(self, dt: float):
        super().tick(dt)
        if not ScreenManager.instance.keyboard_visible:
            self.back()

    @with_db
    def select_account(self, text: str):
        query = select(Account).filter(Account.name == text)
        account = Session().execute(query).scalar_one_or_none()
        if account:
            self.goto(ProfileScreen(account))
        else:
            self.alert(f'Account "{text}" nicht gefunden')
