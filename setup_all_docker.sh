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

cp docker/drinks_touch_xorg.service /etc/systemd/system/
cp docker/xinitrc $HOME

systemctl daemon-reload
systemctl enable --now drinks_touch_xorg.service
export DISPLAY=:0

xhost si:localuser:root
xrandr --output HDMI-1 --rotate left

docker compose -f compose.prod.yaml down
docker compose -f compose.prod.yaml up -d --build
