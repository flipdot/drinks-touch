#!/bin/bash

set -euo pipefail
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "${SCRIPT_DIR}"

if [[ "$UID" != 0 ]];
  echo "Please run me as root."
  exit 1
fi	

cp docker/drinks_touch_xorg.service /etc/systemd/system/
cp docker/xinitrc $HOME

systemctl daemon-reload
systemctl enable --now drinks_touch_xorg.service

docker compose -f compose.prod.yaml up -d
