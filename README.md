# Drinks Scanner Display
Digital replacement for the drinks tally list featuring a touchscreen, user management and a barcode scanner.

## Dependencies
- LDAP server, reachable via `ldap://rail/` (see [users.py](src/users/users.py))
- PostgreSQL @localhost (see [storage.py](src/database/storage.py))
- touch display with a minimum of 480x800 px.

## Database Schema
TODO

## Development

Copy `config.example.py` to `config.py`, customizing the contents.

```bash
sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev
pip2 install -r requirements.txt
echo "password" > mail_pw
systemctl start postgresql
./game.py
```

## Deployment

For embedded systems it is recommended to use `@reboot runGame.sh` inside a cron tab.
This starts an X server, sets various display properties and puts the application itself in a loop.

## License
TODO
