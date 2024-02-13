#!/bin/bash

set -euo pipefail
set -x

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "${SCRIPT_DIR}"

if [[ "$UID" != 0 ]]; then
  echo "Please run me as root."
  exit 1
fi

if [[ ! -f "drinks.env" ]]; then
  echo "Please setup a drinks.env file!!!"
fi

apt-get update
apt-get install -y xserver-xorg-input-evdev rsync

cp docker/drinks_touch_xorg.service /etc/systemd/system/
cp docker/xinitrc "${HOME}"
cp x/99-calibration.conf /etc/X11/xorg.conf.d/

systemctl daemon-reload
systemctl enable --now drinks_touch_xorg.service
export DISPLAY=:0

xhost si:localuser:root
xrandr --output HDMI-1 --rotate left
# Maybe we need to do this every 5 secs
xinput set-prop "eGalax Inc. USB TouchController" "Evdev Axes Swap" "1"
xinput set-prop "eGalax Inc. USB TouchController" "Coordinate Transformation Matrix" 1.3 0 -0.15 0 1.3 -0.15 0 0 1

docker compose -f compose.prod.yaml down
docker compose -f compose.prod.yaml up -d --build
