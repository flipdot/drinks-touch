#!/bin/bash

echo "Starting in 10 seconds!"
sleep 10
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
        cd /home/pi/drinks-scanner-display
        ENV=PI systemd-cat -t"drinks" ./game.py
    )
done
