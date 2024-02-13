#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "Starting in 1 seconds!"
sleep 1
function fix_display () {
    xrandr --output HDMI-1 --rotate left
    xinput set-prop "eGalax Inc. USB TouchController" "Evdev Axes Swap" "1"
    xinput set-prop "eGalax Inc. USB TouchController" "Coordinate Transformation Matrix" 1.3 0 -0.15 0 1.3 -0.15 0 0 1
}
fix_display
while true; do
    sleep 5
    fix_display
done &

while [ 1 ];
do
    (
        set -e
        export ENV=PI
        export PYTHONUNBUFFERED=1

        cd "${SCRIPT_DIR}"
        echo "starting..."
        systemd-cat -t"drinks" ./drinks_touch/game.py
    )
done
