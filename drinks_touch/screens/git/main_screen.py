import functools
import subprocess

import config
from elements import Button, SvgIcon
from elements.hbox import HBox
from elements.vbox import VBox
from screens.git.branch_screen import GitBranchScreen
from screens.git.log_screen import GitLogScreen
from screens.screen import Screen
from screens.tasks_screen import TasksScreen
from tasks import GitFetchTask, UpdateAndRestartTask


class GitMainScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.objects = [
            SvgIcon(
                "drinks_touch/static/images/git-full.svg",
                pos=(10, 20),
                color=config.COLORS["infragelb"],
                height=36,
            ),
            VBox(
                [
                    Button(
                        text="Update & Restart",
                        on_click=functools.partial(
                            self.goto,
                            TasksScreen(
                                self.screen,
                                tasks=[UpdateAndRestartTask()],
                            ),
                        ),
                        size=40,
                    ),
                    HBox(
                        [
                            Button(
                                text="Downgrade",
                                on_click=functools.partial(
                                    self.goto,
                                    GitLogScreen(self.screen, branch="master"),
                                ),
                                size=25,
                            ),
                            Button(
                                text="Branches",
                                on_click=functools.partial(
                                    self.goto, GitBranchScreen(self.screen)
                                ),
                                size=25,
                            ),
                            Button(
                                text="Fetch",
                                on_click=functools.partial(
                                    self.goto,
                                    TasksScreen(
                                        self.screen,
                                        tasks=[GitFetchTask()],
                                        box_height=600,
                                    ),
                                ),
                                size=25,
                            ),
                        ],
                        gap=15,
                    ),
                ],
                pos=(5, 300),
                gap=15,
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

    def update_and_restart(self):
        # git checkout master
        # git merge --ff-only origin/master
        subprocess.run(["git", "checkout", "master"], cwd=config.REPO_PATH)
        subprocess.run(
            ["git", "merge", "--ff-only", "origin/master"], cwd=config.REPO_PATH
        )
