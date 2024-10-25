import functools

from pygit2 import Repository
from pygit2.enums import BranchType

import config
from elements import Label, Button
from elements.vbox import VBox
from screens.git.log_screen import GitLogScreen
from screens.screen import Screen


class GitBranchScreen(Screen):

    def __init__(self, screen):
        super().__init__(screen)
        self.repository = Repository(config.REPO_PATH)

    def on_start(self, *args, **kwargs):
        branch_buttons = [
            Button(
                text=branch,
                on_click=functools.partial(
                    self.goto, GitLogScreen(self.screen, branch=branch)
                ),
                size=20,
            )
            for branch in self.get_branches()
        ]

        self.objects = [
            Label(
                text="git branch",
                pos=(10, 20),
                size=36,
            ),
            VBox(branch_buttons, gap=5, pos=(10, 80)),
            Button(
                text="BACK",
                pos=(5, 795),
                on_click=self.back,
                align_bottom=True,
                font=config.FONTS["monospace"],
                size=30,
            ),
        ]

    def get_branches(self):
        return sorted(self.repository.listall_branches(BranchType.ALL))
