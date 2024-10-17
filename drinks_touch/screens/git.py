import config
from elements import Button
from icons.svg import SvgIcon
from screens.screen import Screen


class GitScreen(Screen):
    def __init__(self, screen):
        super(GitScreen, self).__init__(screen)

        self.objects.append(
            # TODO: Refactor Icon class to be an element
            SvgIcon(
                "drinks_touch/static/images/git.svg",
                color=config.COLORS["infragelb"],
                height=36,
            )
        )

        self.objects.append(
            Button(
                self.screen,
                pos=(50, 600),
                text="Update",
                size=52,
                click_func=self.update,
            )
        )

        self.objects.append(
            Button(
                self.screen,
                pos=(50, 700),
                text="Restart",
                size=52,
                click_func=self.restart,
            )
        )

        self.objects.append(
            Button(
                self.screen,
                pos=(50, 800),
                text="Exit",
                size=52,
                click_func=self.exit,
            )
        )

    def update(self):
        pass

    def restart(self):
        pass

    def exit(self):
        pass
