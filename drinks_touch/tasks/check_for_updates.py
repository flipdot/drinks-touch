from tasks.base import BaseTask


class CheckForUpdatesTask(BaseTask):
    label = "Suche nach drinks-touch updates"

    def run(self):
        super().run()
        self.progress = 1
        self._success()
