# drinks-scanner-display
Strichlisten-Ersatz mit Touchscreen, Usermanagement und Barcodescanner

## Dependencies
- LDAP server, erreichbar unter `ldap://rail/` (siehe [users.py](users/users.py))
- PostgreSQL @localhost (siehe [storage.py](database/storage.py))
- Touchdisplay mit mind. 480x800

## Datenbankschema
TODO

## Development

`config.example.py` nach `config.py` kopieren und ggf. Inhalt anpassen.

    sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev
    pip2 install -r requirements.txt
    echo "password" > mail_pw
    systemctl start postgresql
    ./game.py

## Deployment
Fuer "embedded"-Systeme empfiehlt sich, die `runGame.sh` in einen crontab mit `@reboot` zu schreiben.
Sie startet einen X server, setzt verschiedene Displayeinstellungen, und die Applikation selbst in einer Schleife.

## License
TODO
