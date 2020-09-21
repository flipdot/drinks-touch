#!/bin/bash

set -euo pipefail

if [[ "$#" != 2 ]]; then
  cat <<EOF
Usage: $0 <user_id> <email_address>

EOF
  exit 1
fi 

user_id=$1
mail=$2

function generate() {
  sudo -u postgres psql -AF',' drinks -c ' 
select lu."ldapId",
lu.name,
s.id as "scanevent_id", s.barcode, s.timestamp, s.user_id,
d.name as "getraenk", d.size, d.type
FROM scanevent s
LEFT OUTER JOIN "ldapUsers" lu on lu."ldapId" = s.user_id
LEFT OUTER JOIN drink d on d.ean = s.barcode
WHERE s.user_id = '"'$user_id'"'
ORDER BY timestamp DESC
;'
}

function send() {
  generate | mailx $mail -s 'Your drink report'
}


echo "=== Report Preview ==="
echo
generate | head -n10
echo "======"

echo
echo "OK? then press enter. Otherwise press Ctrl+C"
read
send

