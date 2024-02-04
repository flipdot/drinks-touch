import sys


import ldap3
from ldap3 import Server, Connection, SAFE_SYNC, SUBTREE
import logging
import random
import traceback
from sqlalchemy.sql import text

import config
from database.models.recharge_event import RechargeEvent
from database.storage import get_session

logger = logging.getLogger(__name__)

test_data = [
    {
        "id": b"1",
        "id_card": None,
        "name": b"foo"
    },
    {
        "id": b"2",
        "id_card": b"idcard",
        "name": b"bar"
    },
    {
        "id": b"3",
        "id_card": b"idcard_dm",
        "email": str.encode(config.MAIL_FROM),
        "drinksNotification": "instant",
        "lastDrinkNotification": 0,
        "lastEmailed": 0,
        "name": b"debug_user"
    }
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
            "save": lambda x: x.encode('utf-8') if x else x,
            "load": lambda x: x.decode('utf-8'),
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
            "save": lambda x: x.encode('utf-8'),
            "load": lambda x: x.decode('utf-8'),
        },
        "lastDrinkNotification": {
            "ldap_field": "lastDrinkNotification",
            "index": 0,
            "default": 0,
            "load": float,
            "save": lambda x: str(x).encode()
        },
        "lastEmailed": {
            "ldap_field": "lastEmailed",
            "index": 0,
            "default": 0,
            "load": float,
            "save": lambda x: str(x).encode()
        },
    }
    @staticmethod
    def get_all(filters=None, include_temp=False):
        if filters is None:
            filters = []

        base_dn = 'ou=members,dc=flipdot,dc=org'
        temp_dn = 'ou=temp_members,dc=flipdot,dc=org'
        filters.append("objectclass=person")
        filter_str = "".join(['(' + f.replace(')', '_') + ')' for f in filters])

        if len(filters) > 1:
            filter_str = '(&%s)' % filter_str

        attrs = [k["ldap_field"] for k in Users.fields.values()]
        con = Users.get_ldap_instance()
        _, _, ldap_res, _ = con.search(base_dn, filter_str, search_scope=SUBTREE, attributes=attrs)
        if include_temp:
            _, _, ldap_res2, _ = con.search(temp_dn, filter_str, search_scope=SUBTREE, attributes=attrs)
            ldap_res.extend(ldap_res2)

        users = []
        for ldap_user in ldap_res:
            user = {}
            for drinks_key, meta in Users.fields.items():
                ldap_field = ldap_user['attributes'][meta['ldap_field']]
                if type(ldap_field) is list:

                    ldap_field = next(iter(ldap_field), meta.get('default'))

                user[drinks_key] = ldap_field

            user['path'] = ldap_user['dn']
            users.append(user)

        con.unbind()
        return users

    @staticmethod
    def get_balance(user_id, session=get_session()):
        sql = text("""
                SELECT user_id, count(*) AS amount
                FROM scanevent
                WHERE user_id = :user_id
                GROUP BY user_id
            """)
        row = session.connection().execute(sql, {"user_id": str(user_id)}).fetchone()
        if not row:
            cost = 0
        else:
            cost = row.amount

        sql = text("""
                SELECT user_id, sum(amount) AS amount
                FROM rechargeevent
                WHERE user_id = :user_id
                GROUP BY user_id
            """)
        row = session.connection().execute(sql, {"user_id": str(user_id)}).fetchone()
        if not row:
            credit = 0
        else:
            credit = row.amount

        return credit - cost

    @staticmethod
    def get_recharges(user_id, session=get_session(), limit=None):
        # type: # (str, session) -> RechargeEvent
        q = session.query(RechargeEvent).filter(
            RechargeEvent.user_id == str(user_id)).order_by(
            RechargeEvent.timestamp.desc())
        if limit:
            q = q.limit(limit)
        return q.all()

    @staticmethod
    def get_by_id_card(ean):
        all_users = Users.get_all(filters=['drinksBarcode=' + ean], include_temp=True)
        by_card = dict([(u['id_card'], u) for u in all_users if u['id_card']])
        if ean in by_card:
            return by_card[ean]
        return None

    @staticmethod
    def delete_if_nomoney(user, session=get_session()):
        if not user['path'].endswith(",ou=temp_members,dc=flipdot,dc=org"):
            return
        balance = Users.get_balance(user['id'], session=session)
        if balance <= 0:
            print("deleting user " + str(user['id']) + " because they are broke")
            Users.delete(user)

    @staticmethod
    def delete(user):
        if not user['path'].endswith(",ou=temp_members,dc=flipdot,dc=org"):
            raise ValueError("only temp users allowed")
        try:
            con = Users.get_ldap_instance()
            con.delete(user['path'])
        except Exception as e:
            print("Error: " + str(e))
            exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=4)


    @staticmethod
    def get_ldap_instance():
        dn = "cn=admin,dc=flipdot,dc=org"

        s = Server(config.LDAP_HOST)
        con = Connection(s, dn, config.LDAP_PW,
                         client_strategy=SAFE_SYNC, auto_bind=True)
        return con

    @staticmethod
    def get_by_id(user_id):
        all_users = Users.get_all(filters=['uidNumber=' + str(user_id)], include_temp=True)
        by_id = {u['id']: u for u in all_users if u['id']}
        if str.encode(user_id) in by_id:
            return by_id[str.encode(user_id)]
        return None

    @staticmethod
    def id_to_ean(ean_id):
        return "FDT" + str(ean_id)

    @staticmethod
    def create_temp_user():
        random_id = 30000 + random.randint(1, 2000)
        while Users.get_by_id_card(Users.id_to_ean(random_id)):
            random_id += 1

        barcode = Users.id_to_ean(random_id)
        dn = "cn=" + str(random_id) + ",ou=temp_members,dc=flipdot,dc=org"
        mods = {
            'drinksBarcode': barcode,
            'cn': str(random_id),
            'uid': "geld-" + str(random_id),
            'sn': str(random_id),
        }
        object_class = ["inetOrgPerson", "organizationalPerson", "person", "flipdotter"]
        con = Users.get_ldap_instance()
        con.add(dn, object_class, mods)
        con.unbind()
        return Users.get_by_id_card(barcode)

    @staticmethod
    def set_value(user, drinks_filed, new):
        con = Users.get_ldap_instance()
        con.modify(user['path'], {Users.fields[drinks_filed]['ldap_field']: [(ldap3.MODIFY_REPLACE, new)]})
        con.unbind()

