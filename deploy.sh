#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )


rsync -rv --exclude drinks_touch/config.py --exclude .git --exclude myenv --exclude __pycache__ $SCRIPT_DIR/ pi@drinks.flipdot.space:/home/pi/drinks-touch/
