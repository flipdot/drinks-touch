from database.models.account import Account
from database.storage import init_db


def main():
    init_db()
    Account.sync_all_from_ldap()


main()
