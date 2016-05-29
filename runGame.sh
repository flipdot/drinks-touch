#!/bin/bash
xinput set-prop "eGalax Inc. USB TouchController" "Evdev Axis Calibration" "1701 1641 641 638"
xinput set-prop "eGalax Inc. USB TouchController" "Coordinate Transformation Matrix" 0 1.15 0 1.15 0 0 0 0 1
cd /home/pi/drinks-scanner-display && python game.py
