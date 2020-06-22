import os

from elements.button import Button
from elements.label import Label
from elements.progress import Progress
from notifications.notification import send_drink
from users.users import Users
from .screen import Screen


class SuccessScreen(Screen):
    def __init__(self, screen, user, drink, text, session):
        super(SuccessScreen, self).__init__(screen)

        self.user = user

        self.objects.append(Label(
            self.screen,
            text='Danke,',
            pos=(30, 120),
            size=70
        ))
        self.objects.append(Label(
            self.screen,
            text=bytes.decode(user['name']) + "!",
            pos=(30, 170),
            size=70
        ))
        self.objects.append(Label(
            self.screen,
            text=text,
            size=45,
            pos=(30, 250)
        ))

        self.objects.append(Label(
            self.screen,
            text='Verbleibendes Guthaben: ',
            pos=(30, 350)
        ))
        self.objects.append(Label(
            self.screen,
            text=str(Users.get_balance(self.user['id'], session=session)) + ' EUR',
            pos=(50, 400)
        ))

        self.objects.append(Button(
            self.screen,
            text='OK',
            pos=(50, 600),
            size=50,
            click_func=self.btn_home
        ))

        self.progress = Progress(
            self.screen,
            pos=(400, 500),
            size=80,
            on_elapsed=self.home
        )
        self.objects.append(self.progress)
        self.progress.start()
        balance = Users.get_balance(user['id'])
        if balance >= 0:
            sound = "smb_coin.wav"
        elif balance < -10:
            sound = "alarm.wav"
        else:
            sound = "smb_bowserfalls.wav"
        os.system("ssh -o StrictHostKeyChecking=no pi@pixelfun aplay sounds/%s >/dev/null 2>&1 &" % sound)

        if drink:
            send_drink(user, drink, True)

    @staticmethod
    def home():
        from .screen_manager import ScreenManager
        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()

    def btn_home(self):
        self.home()
