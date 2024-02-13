#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
set -euo pipefail

HOST=drinks.flipdot.space
USER=root
DIR=/opt/drinks-touch

CONN="${USER}@${HOST}"

rsync -rlptv --exclude drinks_touch/config.py --exclude .git --exclude myenv --exclude __pycache__ \
    "${SCRIPT_DIR}/" "${CONN}:${DIR}/"

#shellcheck disable=SC2029
ssh "${CONN}" "cd ${DIR} &&  ./setup_all_docker.sh"

# For future shenanigans
# echo "Please commit first."
# git remote remove pi || :
# git remote add pi root@drinks-touch.flipdot.space:/opt/drinks-touch/.git
# git push pi:from_remote
# ssh root@drinks-touch.flipdot.space "cd /opt/drinks-touch && git merge --ff  && ./setup_all_docker.sh"
