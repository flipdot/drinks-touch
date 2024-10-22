import config
from elements import Label, Button
from screens.screen import Screen


class GitBranchScreen(Screen):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.objects = [
            Label(
                text="git branch",
                pos=(10, 20),
                size=36,
            ),
            Button(
                text="BACK",
                pos=(5, 795),
                on_click=self.back,
                align_bottom=True,
                font=config.FONTS["monospace"],
                size=30,
            ),
        ]
