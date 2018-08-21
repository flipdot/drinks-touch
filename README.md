# Drinks Scanner Display
Digital replacement for the drinks tally list featuring a touchscreen, user management and a barcode scanner.

## Dependencies
- LDAP server, reachable via `ldap://rail/` (see [users.py](users/users.py))
- PostgreSQL @localhost (see [storage.py](database/storage.py))

  > PostgreSQL in Docker:
  > ```
  > docker run --name postgres -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=drinks postgres
  > ```
  >
  > Adminer in Docker:
  > ```
  > docker run -d --link postgres:db -p 8080:8080 adminer
  > ```
- touch display with a minimum of 480x800 px.

## Database Schema
PostgreSQL dumps can be found inside the `sql` folder along with scripts to im- and export.

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
