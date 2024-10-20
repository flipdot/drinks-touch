import config
from elements import Button, SvgIcon
from screens.screen import Screen


class GitScreen(Screen):
    def __init__(self, screen):
        super(GitScreen, self).__init__(screen)

        self.objects = [
            SvgIcon(
                "drinks_touch/static/images/git-full.svg",
                pos=(10, 20),
                color=config.COLORS["infragelb"],
                height=36,
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

    def update(self):
        pass

    def restart(self):
        pass

    def exit(self):
        pass
