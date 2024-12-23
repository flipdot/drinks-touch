import os

from database.models import Account
from elements.label import Label
from notifications.notification import send_drink
from .screen import Screen


class SuccessScreen(Screen):
    idle_timeout = 5

    def __init__(self, account: Account, drink, text, session):
        super().__init__()

        self.account = account
        self.text = text
        self.drink = drink

    def on_start(self, *args, **kwargs):

        self.objects = []
        self.objects.append(Label(text="Danke,", pos=(30, 120), size=70))
        self.objects.append(Label(text=self.account.name + "!", pos=(30, 170), size=70))
        self.objects.append(Label(text=self.text, size=45, pos=(30, 250)))

        self.objects.append(Label(text="Verbleibendes Guthaben: ", pos=(30, 350)))
        self.objects.append(
            Label(
                text=f"{self.account.balance} EUR",
                pos=(50, 400),
            )
        )

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

        if self.drink:
            send_drink(self.account, self.drink, True)
