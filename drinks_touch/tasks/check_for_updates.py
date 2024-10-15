from tasks.base import BaseTask
import threading
import requests


class CheckForUpdatesTask(BaseTask):
    label = "Suche nach drinks-touch updates"
    newest_version_sha_short = ""
    newest_version_lock = threading.Lock()

    def run(self):
        global newest_version_sha_short

        # download latest commit sha from github
        request_url = "https://api.github.com/repos/flipdot/drinks-touch/commits/master?per_page=1"
        self.output += f"Requesting {request_url}\n"
        response = requests.get(
            request_url,
            timeout=5,
        )
        response.raise_for_status()
        json = response.json()
        self.output += f"Response: {response.status_code}\n"
        self.output += f"Latest: {json['sha']}"

        with CheckForUpdatesTask.newest_version_lock:
            CheckForUpdatesTask.newest_version_sha_short = json["sha"][:7]
