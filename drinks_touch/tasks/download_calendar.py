import requests

import config
from tasks.base import BaseTask


class DownloadCalendarTask(BaseTask):
    LABEL = "Lade Kalender herunter"

    def run(self):
        self.logger.info("Downloaded fd event calendar")

        response = requests.get(config.ICAL_URL)
        response.raise_for_status()

        if not config.ICAL_FILE_PATH.parent.exists():
            config.ICAL_FILE_PATH.parent.mkdir(parents=True)

        with open(config.ICAL_FILE_PATH, "wb") as f:
            f.write(response.content)

        self.logger.info(f"Written to {config.ICAL_FILE_PATH}")
