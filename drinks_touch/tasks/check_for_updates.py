from tasks.base import BaseTask
import threading
import requests


class CheckForUpdatesTask(BaseTask):
    LABEL = "Suche nach drinks-touch updates"
    ON_STARTUP = True
    newest_version_sha_short = ""
    newest_version_lock = threading.Lock()

    def run(self):
        # download latest commit sha from github
        request_url = (
            "https://code.flipdot.org/api/v1/repos/flipdot/drinks-touch/branches/main"
        )
        self.logger.info(f"GET {request_url}")
        response = requests.get(
            request_url,
            timeout=5,
        )
        response.raise_for_status()
        json = response.json()
        sha = json["commit"]["id"]
        self.logger.info(f"Response: {response.status_code}")
        self.logger.info(f"Latest: {sha}")

        with CheckForUpdatesTask.newest_version_lock:
            CheckForUpdatesTask.newest_version_sha_short = sha[:7]
