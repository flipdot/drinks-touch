import sys


from ldap3 import Server, Connection, SAFE_SYNC, SUBTREE
import logging
import traceback

import config
from database.storage import get_session, Session

logger = logging.getLogger(__name__)

test_data = [
    {"id": b"1", "id_card": None, "name": b"foo"},
    {"id": b"2", "id_card": b"idcard", "name": b"bar"},
    {
        "id": b"3",
        "id_card": b"idcard_dm",
        "email": str.encode(config.MAIL_FROM),
        "drinksNotification": "instant",
        "lastDrinkNotification": 0,
        "lastEmailed": 0,
        "name": b"debug_user",
    },
]


class Users(object):
    def __init__(self):
        pass

    # Keys: Us, Values: LDAP
    fields = {
        "name": {
            "ldap_field": "uid",
            "index": 0,
        },
        "id": {
            "ldap_field": "uidNumber",
        },
        "id_card": {
            "ldap_field": "drinksBarcode",
            "index": 0,
            "default": None,
        },
        "email": {
            "ldap_field": "mail",
            "index": 0,
            "default": None,
        },
        "drinksNotification": {
            "ldap_field": "drinksNotification",
            "index": 0,
            "default": "instant",
        },
        "lastDrinkNotification": {
            "ldap_field": "lastDrinkNotification",
            "index": 0,
            "default": 0,
            "load": float,
            "save": str,
        },
        "lastEmailed": {
            "ldap_field": "lastEmailed",
            "index": 0,
            "default": 0,
            "load": float,
            "save": str,
        },
    }

    @staticmethod
    def get_all(filters=None, include_temp=False) -> list[dict]:
        logger = logging.getLogger("SyncFromLDAPTask")
        if filters is None:
            filters = []

        base_dn = "ou=members,dc=flipdot,dc=org"
        temp_dn = "ou=temp_members,dc=flipdot,dc=org"
        filters.append("objectclass=person")
        filter_str = "".join(["(" + f.replace(")", "_") + ")" for f in filters])

        if len(filters) > 1:
            filter_str = "(&%s)" % filter_str

        logger.info("Searching %s", base_dn)

        attrs = [k["ldap_field"] for k in Users.fields.values()]
        con = Users.get_ldap_instance()
        _, _, ldap_res, _ = con.search(
            base_dn, filter_str, search_scope=SUBTREE, attributes=attrs
        )
        logger.info("Found %d members", len(ldap_res))
        if include_temp:
            logger.info("Searching %s", temp_dn)
            _, _, ldap_res2, _ = con.search(
                temp_dn, filter_str, search_scope=SUBTREE, attributes=attrs
            )
            ldap_res.extend(ldap_res2)
            logger.info("Found %d tmp users", len(ldap_res2))

        logger.info("Found %d total users", len(ldap_res))
        users = []
        for ldap_user in ldap_res:
            user = {}
            for drinks_key, meta in Users.fields.items():
                ldap_field = ldap_user["attributes"][meta["ldap_field"]]
                if type(ldap_field) is list:
                    ldap_field = next(iter(ldap_field), meta.get("default"))
                    if "load" in meta:
                        ldap_field = meta["load"](ldap_field)

                user[drinks_key] = ldap_field

            user["path"] = ldap_user["dn"]
            users.append(user)

        con.unbind()
        return users

    @staticmethod
    def get_balance(user_id, session=None) -> int | None:
        from database.models.account import Account

        account = (
            Session().query(Account).filter(Account.ldap_id == str(user_id)).first()
        )
        if not account:
            return None
        return account.balance

    @staticmethod
    def get_by_id_card(ean):
        all_users = Users.get_all(filters=["drinksBarcode=" + ean], include_temp=True)
        by_card = dict([(u["id_card"], u) for u in all_users if u["id_card"]])
        if ean in by_card:
            return by_card[ean]
        return None

    @staticmethod
    def delete_if_nomoney(user, session=None):
        if session is None:
            session = get_session()
        if not user["path"].endswith(",ou=temp_members,dc=flipdot,dc=org"):
            return
        balance = Users.get_balance(user["id"], session=session)
        if balance <= 0:
            print("deleting user " + str(user["id"]) + " because they are broke")
            Users.delete(user)

    @staticmethod
    def delete(user):
        if not user["path"].endswith(",ou=temp_members,dc=flipdot,dc=org"):
            raise ValueError("only temp users allowed")
        try:
            con = Users.get_ldap_instance()
            con.delete(user["path"])
        except Exception as e:
            print("Error: " + str(e))
            exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=4)

    @staticmethod
    def get_ldap_instance():
        dn = config.LDAP_USER

        s = Server(config.LDAP_HOST)
        con = Connection(
            s, dn, config.LDAP_PW, client_strategy=SAFE_SYNC, auto_bind=True
        )
        return con

    @staticmethod
    def get_by_id(user_id):
        all_users = Users.get_all(
            filters=["uidNumber=" + str(user_id)], include_temp=True
        )
        by_id = {str(u["id"]): u for u in all_users if u["id"]}
        if user_id in by_id:
            return by_id[user_id]
        return None
