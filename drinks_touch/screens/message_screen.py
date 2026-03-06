import config
from elements import Label, Button, Image
from elements.vbox import VBox
from screens.screen import Screen
from screens.tasks_screen import TasksScreen
from tasks.run_cmd import RestartTask


class MessageScreen(Screen):

    def __init__(
        self,
        title: str,
        message: list[str],
        logo: str | None = None,
        buttons: list[dict] | None = None,
        button_size: int = 40,
    ):
        super().__init__()
        self.objects = [
            Label(
                text=title,
                pos=(5, 5),
            ),
        ]
        y = 80  # Standard spacing from title to content
        if logo:
            logo_img = Image(src=logo)
            # scale logo to fit screen width if too large
            if logo_img.width > config.SCREEN_WIDTH - 10:
                scale = (config.SCREEN_WIDTH - 10) / logo_img.width
                logo_img = Image(
                    src=logo,
                    size=(int(logo_img.width * scale), int(logo_img.height * scale)),
                )

            logo_img.pos = ((config.SCREEN_WIDTH - logo_img.width) // 2, y)
            self.objects.append(logo_img)
            y += logo_img.height + 20

        self.objects.append(
            VBox(
                [
                    Label(
                        text=s,
                        size=15,
                        font=config.Font.MONOSPACE,
                    )
                    for s in message
                ],
                pos=(5, y),
            )
        )

        if buttons is None:
            buttons = [
                {
                    "text": "Reboot",
                    "on_click": lambda: self.goto(
                        TasksScreen(
                            tasks=[RestartTask()],
                        ),
                    ),
                },
                {
                    "text": "Ignorieren",
                    "on_click": self.home,
                },
            ]

        self.objects.append(
            VBox(
                [
                    Button(
                        text=b["text"],
                        on_click=b["on_click"],
                        size=button_size,
                        width=config.SCREEN_WIDTH - 60,
                    )
                    for b in buttons
                ],
                align_bottom=True,
                gap=30,
                pos=(30, config.SCREEN_HEIGHT - 80),
            )
        )
