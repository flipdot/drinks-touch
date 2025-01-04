import config
from elements import Label
from elements.input_field import InputField, InputType
from elements.spacer import Spacer
from elements.vbox import VBox
from screens.screen import Screen


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
                        text="An wen möchtest du Guthaben übertragen?",
                        size=20,
                    ),
                    InputField(
                        width=config.SCREEN_WIDTH - 10,
                        height=50,
                    ),
                    Spacer(height=40),
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
                        text="- Auto-complete des Namens",
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
