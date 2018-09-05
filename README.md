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
docker run --name dsd_postgres -d -p 5432:5432 -v dsd_postgres-data:/var/lib/postgresql/data -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=drinks postgres

# Adminer
docker run --name dsd_adminer -d -p 8080:8080 --link dsd_postgres:db adminer
```
Login to the [dashboard](http://localhost:8080) with **database system**, **username** and **password** `postgres`, **server** `dsd_postgres` and **database** `drinks`.

```bash
# OpenLDAP
docker run --name dsd_ldap -d -p 389:389 -e LDAP_DOMAIN="flipdot.org" osixia/openldap

# PHPLDAPAdmin
docker run --name dsd_phpldapadmin -d -p 6443:443 -v dsd_phpldapadmin-data:/var/www/phpldapadmin --link dsd_ldap:ldap -e PHPLDAPADMIN_LDAP_HOSTS=ldap osixia/phpldapadmin
```
Login to the [dashboard](https://localhost:6443) with **login dn** `cn=admin,dc=flipdot,dc=org` and **password** `admin`.

And finally, run the entrypoint script `game.py`.

## Deployment

For embedded systems it is recommended to use `@reboot runGame.sh` inside a cron tab.
This starts an X server, sets various display properties and puts the application itself in a loop.

## License
TODO
