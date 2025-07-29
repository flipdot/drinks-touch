from pygame.mixer import Sound

import config
from elements import Button, SvgIcon, Label
from elements.hbox import HBox
from elements.vbox import VBox
from screens.screen_manager import ScreenManager
from screens.settings.git_branch_screen import GitBranchScreen
from screens.screen import Screen
from screens.tasks_screen import TasksScreen
from tasks import (
    UpdateAndRestartTask,
    SepaSyncTask,
    SendMailTask,
    SyncFromKeycloakTask,
    InitializeBarcodeScannerTask,
)


class SettingsMainScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.soundcheck = False
        self.clock = 0
        self.sound = Sound("drinks_touch/resources/sounds/smb_pipe.wav")

        icon_text_gap = 15

        button_width = config.SCREEN_WIDTH - 10
        self.objects = [
            Label(
                text="Einstellungen",
                pos=(5, 5),
            ),
            VBox(
                [
                    HBox(
                        [
                            Button(
                                on_click=lambda: self.go_if_git(
                                    TasksScreen(
                                        tasks=[UpdateAndRestartTask()],
                                    ),
                                ),
                                inner=HBox(
                                    [
                                        SvgIcon(
                                            "drinks_touch/resources/images/arrow-up-circle.svg",
                                            height=40,
                                            color=config.Color.PRIMARY,
                                        ),
                                        Label(text="Update"),
                                    ],
                                    gap=icon_text_gap,
                                ),
                                width=button_width / 2 - 15,
                            ),
                            Button(
                                on_click=lambda: self.go_if_git(GitBranchScreen()),
                                inner=HBox(
                                    [
                                        SvgIcon(
                                            "drinks_touch/resources/images/git-branch.svg",
                                            height=40,
                                            color=config.Color.PRIMARY,
                                        ),
                                        Label(text="Branches"),
                                    ],
                                    gap=icon_text_gap,
                                ),
                                width=button_width / 2,
                            ),
                        ],
                        gap=15,
                    ),
                    Button(
                        on_click=lambda: self.goto(TasksScreen()),
                        inner=HBox(
                            [
                                SvgIcon(
                                    "drinks_touch/resources/images/refresh-cw.svg",
                                    height=40,
                                    color=config.Color.PRIMARY,
                                ),
                                Label(text="Neu initialisieren"),
                            ],
                            gap=icon_text_gap,
                        ),
                        width=button_width,
                    ),
                    Button(
                        on_click=self.toggle_soundcheck,
                        pass_on_click_kwargs=True,
                        inner=HBox(
                            [
                                SvgIcon(
                                    "drinks_touch/resources/images/volume-x.svg",
                                    height=40,
                                    color=config.Color.PRIMARY,
                                ),
                                Label(text="Soundcheck"),
                            ],
                            gap=icon_text_gap,
                        ),
                        width=button_width,
                    ),
                    Button(
                        on_click=lambda: self.goto(
                            TasksScreen(tasks=[InitializeBarcodeScannerTask()])
                        ),
                        inner=HBox(
                            [
                                SvgIcon(
                                    "drinks_touch/resources/images/barcode.svg",
                                    height=40,
                                    color=config.Color.PRIMARY,
                                ),
                                Label(text="Barcode-Scanner Init"),
                            ],
                            gap=icon_text_gap,
                        ),
                        width=button_width,
                    ),
                    # Transaction migration was done already.
                    # Keeping it here as long as we have the old data model still in place
                    # Button(
                    #     on_click=lambda: self.goto(
                    #         TasksScreen(tasks=[MigrateTxTask()])
                    #     ),
                    #     text="Migriere Transaktionen",
                    # ),
                    Button(
                        on_click=lambda: self.goto(TasksScreen(tasks=[SepaSyncTask()])),
                        inner=HBox(
                            [
                                SvgIcon(
                                    "drinks_touch/resources/images/euro.svg",
                                    height=40,
                                    color=config.Color.PRIMARY,
                                ),
                                Label(text="SEPA Sync"),
                            ],
                            gap=icon_text_gap,
                        ),
                        width=button_width,
                    ),
                    Button(
                        on_click=lambda: self.goto(TasksScreen(tasks=[SendMailTask()])),
                        inner=HBox(
                            [
                                SvgIcon(
                                    "drinks_touch/resources/images/mail.svg",
                                    height=40,
                                    color=config.Color.PRIMARY,
                                ),
                                Label(text="Mails versenden"),
                            ],
                            gap=icon_text_gap,
                        ),
                        width=button_width,
                    ),
                    Button(
                        on_click=lambda: self.goto(
                            TasksScreen(tasks=[SyncFromKeycloakTask()])
                        ),
                        inner=HBox(
                            [
                                SvgIcon(
                                    "drinks_touch/resources/images/users.svg",
                                    height=40,
                                    color=config.Color.PRIMARY,
                                ),
                                Label(text="Account Sync"),
                            ],
                            gap=icon_text_gap,
                        ),
                        width=button_width,
                    ),
                    Button(
                        on_click=self.toggle_debug,
                        pass_on_click_kwargs=True,
                        inner=HBox(
                            [
                                SvgIcon(
                                    "drinks_touch/resources/images/bug.svg",
                                    height=40,
                                    color=config.Color.PRIMARY,
                                ),
                                Label(
                                    text=f"Debug {ScreenManager.instance.DEBUG_LEVEL}"
                                ),
                            ],
                            gap=icon_text_gap,
                        ),
                        width=button_width,
                    ),
                ],
                pos=(5, 70),
                gap=15,
            ),
        ]

    def toggle_debug(self, button: Button):
        ScreenManager.instance.DEBUG_LEVEL += 1
        if ScreenManager.instance.DEBUG_LEVEL > ScreenManager.instance.MAX_DEBUG_LEVEL:
            ScreenManager.instance.DEBUG_LEVEL = 0
        button.inner[1].text = f"Debug {ScreenManager.instance.DEBUG_LEVEL}"

    def go_if_git(self, screen: Screen):
        if config.GIT_REPO_AVAILABLE:
            self.goto(screen)
        else:
            self.alert("Nur verfügbar, wenn git Repo vorhanden")

    def toggle_soundcheck(self, button: Button):
        self.soundcheck = not self.soundcheck
        img_dir_path = button.inner[0].path.parent
        if self.soundcheck:
            button.inner[0].path = img_dir_path / "volume-2.svg"
            button.inner[1].text = "Soundcheck aus"
        else:
            button.inner[0].path = img_dir_path / "volume-x.svg"
            button.inner[1].text = "Soundcheck"

    def tick(self, dt: float):
        super().tick(dt)
        self.clock += dt
        if self.soundcheck and self.clock > 1.5:
            self.sound.play()
            self.clock = 0
