import subprocess

from pygame.mixer import Sound

import config
from elements import Button, SvgIcon, Label
from elements.hbox import HBox
from elements.vbox import VBox
from screens.settings.git_branch_screen import GitBranchScreen
from screens.settings.git_log_screen import GitLogScreen
from screens.screen import Screen
from screens.tasks_screen import TasksScreen
from tasks import GitFetchTask, UpdateAndRestartTask


class SettingsMainScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.soundcheck = False
        self.clock = 0
        self.sound = Sound("drinks_touch/resources/sounds/smb_pipe.wav")

        self.soundcheck_button = Button(
            on_click=self.toggle_soundcheck,
            inner=HBox(
                [
                    SvgIcon(
                        "drinks_touch/resources/images/volume-x.svg",
                        height=30,
                        color=config.Color.PRIMARY,
                    ),
                    Label(text="Soundcheck", size=25),
                ]
            ),
        )

        self.objects = [
            Label(
                text="Einstellungen",
                pos=(5, 5),
            ),
            VBox(
                [
                    Button(
                        text="Update & Restart",
                        on_click=lambda: self.go_if_git(
                            TasksScreen(
                                tasks=[UpdateAndRestartTask()],
                            ),
                        ),
                        size=40,
                    ),
                    HBox(
                        [
                            Button(
                                text="Downgrade",
                                on_click=lambda: self.go_if_git(
                                    GitLogScreen(branch="master")
                                ),
                                size=25,
                            ),
                            Button(
                                text="Branches",
                                on_click=lambda: self.go_if_git(GitBranchScreen()),
                                size=25,
                            ),
                            Button(
                                text="Fetch",
                                on_click=lambda: self.go_if_git(
                                    TasksScreen(
                                        tasks=[GitFetchTask()],
                                        box_height=600,
                                    ),
                                ),
                                size=25,
                            ),
                        ],
                        gap=15,
                    ),
                    self.soundcheck_button,
                    Button(
                        on_click=lambda: self.goto(TasksScreen()),
                        inner=HBox(
                            [
                                SvgIcon(
                                    "drinks_touch/resources/images/refresh-cw.svg",
                                    height=30,
                                    color=config.Color.PRIMARY,
                                ),
                                Label(text="Neu initialisieren", size=25),
                            ]
                        ),
                    ),
                ],
                pos=(5, 300),
                gap=15,
            ),
        ]

    def go_if_git(self, screen: Screen):
        if config.GIT_REPO_AVAILABLE:
            self.goto(screen)
        else:
            self.alert("Nur verfügbar, wenn git Repo vorhanden")

    def toggle_soundcheck(self):
        self.soundcheck = not self.soundcheck
        img_dir_path = self.soundcheck_button.inner[0].path.parent
        height = self.soundcheck_button.inner[0].height
        color = self.soundcheck_button.inner[0].color
        if self.soundcheck:
            self.soundcheck_button.inner[0] = SvgIcon(
                img_dir_path / "volume-2.svg", height=height, color=color
            )
            self.soundcheck_button.inner[1].text = "Soundcheck aus"
        else:
            self.soundcheck_button.inner[0] = SvgIcon(
                img_dir_path / "volume-x.svg", height=height, color=color
            )
            self.soundcheck_button.inner[1].text = "Soundcheck"

    def render(self, dt):
        self.clock += dt
        if self.soundcheck and self.clock > 1.5:
            self.sound.play()
            self.clock = 0
        return super().render(dt)

    def update_and_restart(self):
        # git checkout master
        # git merge --ff-only origin/master
        subprocess.run(["git", "checkout", "master"], cwd=config.REPO_PATH)
        subprocess.run(
            ["git", "merge", "--ff-only", "origin/master"], cwd=config.REPO_PATH
        )
