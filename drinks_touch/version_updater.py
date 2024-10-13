import threading
import requests

newest_version_sha_short = ""
newest_version_lock = threading.Lock()


def check_for_updates():
    global newest_version_sha_short
    global newest_version_lock

    # download latest commit sha from github
    response = requests.get(
        "https://api.github.com/repos/flipdot/drinks-touch/commits/master?per_page=1",
        timeout=5,
    )
    response.raise_for_status()

    with newest_version_lock:
        newest_version_sha_short = response.json()["sha"][:7]
