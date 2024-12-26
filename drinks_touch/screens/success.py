import os

import config
from database.models import Account
from elements import Button
from elements.label import Label
from elements.vbox import VBox
from notifications.notification import send_drink
from .screen import Screen


class SuccessScreen(Screen):
    idle_timeout = 5

    def __init__(self, account: Account, drink, text):
        super().__init__()

        self.account = account
        self.text = text
        self.drink = drink

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
            VBox(
                [
                    Label(text="Danke!", size=70),
                    Label(text=self.text, size=20),
                ],
                pos=(5, 100),
            ),
            Button(
                text="OK",
                on_click=self.home,
                size=50,
                pos=(200, config.SCREEN_HEIGHT - 100),
                align_bottom=True,
            ),
        ]

        # TODO: Sound is currently not working, and happening synchronously,
        #            therefore slowing down the UI
        # self.play_sound()

        if self.drink:
            send_drink(self.account, self.drink, True)

    def play_sound(self):
        balance = self.account.balance
        if balance >= 0:
            sound = "smb_coin.wav"
        elif balance < -10:
            sound = "alarm.wav"
        else:
            sound = "smb_bowserfalls.wav"

        os.system(
            "ssh -o StrictHostKeyChecking=no pi@pixelfun aplay sounds/%s >/dev/null 2>&1 &"
            % sound
        )
