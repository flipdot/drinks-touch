import config
from elements import Label, Button
from elements.hbox import HBox
from elements.vbox import VBox
from screens.screen import Screen
from screens.tasks_screen import TasksScreen
from tasks.run_cmd import RestartTask


class MessageScreen(Screen):

    def __init__(self, title: str, message: list[str]):
        super().__init__()
        self.objects = [
            Label(
                text=title,
                pos=(5, 5),
            ),
            VBox(
                [
                    Label(
                        text=s,
                        size=15,
                        font=config.Font.MONOSPACE,
                    )
                    for s in message
                ],
                pos=(5, 80),
            ),
            HBox(
                [
                    Button(
                        text="Reboot",
                        on_click=lambda: self.goto(
                            TasksScreen(
                                tasks=[RestartTask()],
                            ),
                        ),
                        size=40,
                    ),
                    Button(
                        text="Ignorieren",
                        on_click=self.home,
                        size=40,
                    ),
                ],
                align_bottom=True,
                pos=(30, config.SCREEN_HEIGHT - 80),
            ),
        ]
