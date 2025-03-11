#!/bin/bash

KEYS=(
    -r B04800CE
    -r 08B0AE86
)
    # expired: -r 99CABD50
MAIL=(
    vorstand@flipdot.org
    c+drinks@cfs.im
)
export FROM=flipdot-noti@vega.uberspace.de
SUBJECT="Drinks Report"

tmp=$(mktemp)
exec > >(tee $tmp) 2>*1
function send_cleanup() {
    gpg -ea "${KEYS[@]}" --always-trust -o - < "$tmp" \
        | mailx -r "$FROM" -s "$SUBJECT" "${MAIL[@]}"
    rm -f "$tmp"*
}
trap send_cleanup EXIT TERM INT

sudo -u postgres psql drinks < docs/auflandungs_stats.sql |head -n10 >> "$tmp"
