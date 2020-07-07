#!/bin/bash

echo "Starting in 5 seconds!"
sleep 5
function fix_display () {
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

        cd /home/pi/drinks-touch
        echo "starting..."
        systemd-cat -t"drinks" ./drinks_touch/game.py
    )
done
