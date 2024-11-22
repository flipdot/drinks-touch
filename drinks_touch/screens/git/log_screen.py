import functools
from dataclasses import dataclass
from datetime import datetime

import config
from elements import Label, Button
from elements.hbox import HBox
from elements.vbox import VBox
from screens.screen import Screen
from pygit2 import Repository

from screens.tasks_screen import TasksScreen
from tasks.base import logger
from tasks.run_cmd import CheckoutAndRestartTask

# Git screen was introduced at this date.
# Don't allow the user to checkout commits before this date,
# otherwise they can't upgrade again via the UI.
DATE_SINCE_GITSCREEN = datetime(2024, 10, 25)


@dataclass
class Commit:
    sha: str
    title: str
    full_message: str
    author: str
    date: datetime


class GitLogScreen(Screen):

    def __init__(self, branch: str):
        super().__init__()

        self.branch = branch
        self.repository = Repository(config.REPO_PATH)

    def on_start(self, *args, **kwargs):

        commit_buttons = [
            HBox(
                [
                    Button(
                        text=f"Checkout {commit.sha[:7]}",
                        on_click=functools.partial(self.checkout, commit),
                        size=15,
                        color=(
                            color := (
                                config.Color.PRIMARY
                                if commit.date >= DATE_SINCE_GITSCREEN
                                else config.COLORS["disabled"]
                            )
                        ),
                    ),
                    VBox(
                        [
                            Label(
                                text=f"{commit.date.strftime('%Y-%m-%d %H:%M:%S')} {commit.author}",
                                size=15,
                                color=color,
                            ),
                            Label(
                                text=commit.title,
                                size=10,
                                color=color,
                            ),
                        ]
                    ),
                ]
            )
            for commit in self.get_commits(12)
        ]
        self.objects = [
            Label(
                text=f"git log {self.branch}",
                pos=(10, 20),
                size=36,
            ),
            VBox(
                commit_buttons,
                pos=(10, 70),
                gap=16,
            ),
        ]

    def get_commits(self, max_num=None) -> list[Commit]:
        reference = self.repository.lookup_reference_dwim(self.branch)
        commits = []
        for commit in self.repository.walk(reference.target):
            commits.append(
                Commit(
                    sha=str(commit.id),
                    title=commit.message.split("\n")[0],
                    full_message=commit.message,
                    author=commit.author.name,
                    date=datetime.fromtimestamp(commit.commit_time),
                )
            )
            if max_num is not None and len(commits) >= max_num:
                break
        return commits

    def checkout(self, commit: Commit):
        if commit.date < DATE_SINCE_GITSCREEN:
            logger.info("Can't checkout commits before Git screen was introduced.")
            return
        self.goto(TasksScreen([CheckoutAndRestartTask(commit.sha)]))
