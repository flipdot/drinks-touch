# Drinks Scanner Display
Digital replacement for the drinks tally list featuring a touchscreen, user management and a barcode scanner.

## Dependencies
- LDAP server, reachable via `ldap://rail/` (see [users.py](users/users.py))
- PostgreSQL @localhost (see [storage.py](database/storage.py))
- touch display with a minimum of 480x800 px.

## Database Schema
PostgreSQL dumps can be found inside the `sql` folder along with scripts to im- and export.

## Development

Install dependencies like this:

```bash
sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev
pip2 install -r requirements.txt
```
Then copy `config.example.py` to `config.py`, customizing the contents.

Now, start PostgreSQL and OpenLDAP either with `systemctl start` or with Docker:

```bash
# PostgreSQL
docker run --name postgres -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=drinks postgres

# Adminer
docker run --name adminer -d -p 8080:8080 --link postgres:db adminer
```


```bash
# OpenLDAP
docker run --name openldap -d -p 389:389 -e LDAP_DOMAIN="flipdot.org" osixia/openldap

# PHPLDAPAdmin
docker run --name phpldapadmin -d -p 6443:443 --link openldap:ldap -e PHPLDAPADMIN_LDAP_HOSTS=ldap osixia/phpldapadmin
```

And finally, run the entrypoint script `game.py`.

## Deployment

For embedded systems it is recommended to use `@reboot runGame.sh` inside a cron tab.
This starts an X server, sets various display properties and puts the application itself in a loop.

## License
TODO
