from elements import Label, Progress
from elements.progress_bar import ProgressBar
from .screen import Screen

LOREM = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in
reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
"""


class SyncScreen(Screen):

    def __init__(self, screen):
        super(SyncScreen, self).__init__(screen)
        self.progess_bar = ProgressBar(
            self.screen,
            pos=(10, 350),
            label="Syncing",
            text=LOREM,
        )

        self.objects = [
            Label(
                self.screen,
                text="Sync",
                pos=(50, 50),
            ),
            Progress(
                self.screen,
                pos=(50, 150),
                speed=1 / 5,
                on_elapsed=self.time_elapsed,
            ),
            self.progess_bar,
        ]

    def time_elapsed(self):
        # from screens.screen_manager import ScreenManager

        # self.progess_bar.success()
        self.progess_bar.fail()

        # self.progess_bar.percent = 0.9

        # screen_manager = ScreenManager.get_instance()
        # screen_manager.set_default()
