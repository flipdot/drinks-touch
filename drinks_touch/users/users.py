import sys

import json
import ldap
import ldap.modlist as modlist
import logging
import random
import traceback
from sqlalchemy.sql import text

import config
from database.models.recharge_event import RechargeEvent
from database.storage import get_session
from env import is_pi

logger = logging.getLogger(__name__)

test_data = [
    {
        "id": "1",
        "id_card": None,
        "name": "foo"
    },
    {
        "id": "2",
        "id_card": "idcard",
        "name": "bar"
    },
    {
        "id": "3",
        "id_card": "idcard_dm",
        "email": config.MAIL_FROM,
        "meta": {
            "drink_notification": "instant",
            "last_drink_notification": 0,
            "last_emailed": 0
        },
        "name": "debug_user"
    }
]


class Users(object):
    active_user = None

    def __init__(self):
        pass

    # Keys: Us, Values: LDAP
    fields = {
        "path": {
            "ldap_field": "path",
        },
        "name": {
            "ldap_field": "uid",
            "index": 0,
        },
        "id": {
            "ldap_field": "uidNumber",
            "index": 0,
        },
        "id_card": {
            "ldap_field": "carLicense",
            "index": 0,
            "default": None,
        },
        "email": {
            "ldap_field": "mail",
            "index": 0,
            "default": None,
        },
        "meta": {
            "ldap_field": "postOfficeBox",
            "index": 0,
            "default": {
                "drink_notification": "instant",
                # instant, daily, weekly, never
                "last_drink_notification": 0,
                "last_emailed": 0,
            },
            "load": json.loads,
            "save": json.dumps,
        },
        "lastEmailed": {
            "ldap_field": "telexNumber",
            "index": 0,
            "default": 0.0,
            "load": float,
            "save": str,
        },
    }

    @staticmethod
    def get_all(prefix='', filters=None, include_temp=False):
        if filters is None:
            filters = []

        try:
            users = []
            ldap_users = Users.read_all_users_ldap(filters, include_temp)

            for ldap_user in ldap_users:
                name = ldap_user['uid'][0]

                if prefix != '' and name.lower().startswith(
                        prefix.lower()) is False:
                    continue

                user = Users.user_from_ldap(ldap_user)
                users.append(user)

            return users
        except Exception:
            if not is_pi():
                logger.warning("ldap fail, falling back to test data.")
                return filter(
                    lambda u: prefix == '' or u['name'].lower().startswith(
                        prefix.lower()), test_data)
            else:
                raise

    @staticmethod
    def user_from_ldap(ldap_user):
        user = {}
        for key, meta in Users.fields.items():
            try:
                value = ldap_user[meta['ldap_field']]
                if "index" in meta:
                    value = value[meta["index"]]
                if "load" in meta:
                    value = meta['load'][value]
                if value is None and "default" in meta:
                    value = meta["default"]
                user[key] = value
            except Exception:
                if 'default' in meta:
                    user[key] = meta['default']
                else:
                    raise
        user["_reference"] = {}
        for key, meta in Users.fields.items():
            value = user[key]
            if "save" in meta:
                value = meta["save"][value]
            user["_reference"][key] = value
        if user['id_card']:
            user['id_card'] = user['id_card'].upper()
        Users.save(user)
        return user

    @staticmethod
    def get_ldap_instance():
        dn = "cn=admin,dc=flipdot,dc=org"

        con = ldap.initialize(config.LDAP_HOST)
        con.simple_bind_s(dn, config.LDAP_PW)
        return con

    @staticmethod
    def read_all_users_ldap(filters=None, include_temp=False):
        if filters is None:
            filters = []

        base_dn = 'ou=members,dc=flipdot,dc=org'
        temp_dn = 'ou=temp_members,dc=flipdot,dc=org'
        attrs = [k["ldap_field"] for k in Users.fields.values()]
        filters.append("objectclass=person")

        filter_str = "".join(['(' + f.replace(')', '_') + ')' for f in filters])
        if len(filters) > 1:
            filter_str = '(&%s)' % filter_str

        con = Users.get_ldap_instance()
        ldap_res = con.search_s(base_dn, ldap.SCOPE_SUBTREE, filter_str, attrs)
        if include_temp:
            ldap_res.extend(
                con.search_s(temp_dn, ldap.SCOPE_SUBTREE, filter_str, attrs))

        users = []
        for path, user in ldap_res:
            if 'uidNumber' not in user:
                user['uidNumber'] = user['uid']
            if 'carLicense' not in user:
                user['carLicense'] = [None]
            user['path'] = path
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
        row = session.connection().execute(sql, user_id=user_id).fetchone()
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
        # print(sql, user_id)
        row = session.connection().execute(sql, user_id=user_id).fetchone()
        if not row:
            credit = 0
        else:
            credit = row.amount

        return credit - cost

    @staticmethod
    def get_recharges(user_id, session=get_session(), limit=None):
        # type: # (str, session) -> RechargeEvent
        q = session.query(RechargeEvent).filter(
            RechargeEvent.user_id == user_id).order_by(
            RechargeEvent.timestamp.desc())
        if limit:
            q = q.limit(limit)
        return q.all()

    @staticmethod
    def set_value(user, field, value, create_field=False):
        con = Users.get_ldap_instance()
        if value:
            add_pass = [(ldap.MOD_ADD if create_field else ldap.MOD_REPLACE,
                         field, [value])]
        else:
            add_pass = [(ldap.MOD_DELETE, field, [])]
        con.modify_s(user['path'], add_pass)

    @staticmethod
    def get_by_id(user_id):
        all_users = Users.get_all(filters=['uidNumber=' + str(user_id)], include_temp=True)
        by_id = {u['id']: u for u in all_users if u['id']}
        if user_id in by_id:
            return by_id[user_id]
        return None

    @staticmethod
    def get_by_id_card(ean):
        all_users = Users.get_all(filters=['carLicense=' + ean], include_temp=True)
        by_card = dict([(u['id_card'], u) for u in all_users if u['id_card']])
        if ean in by_card:
            return by_card[ean]
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
            'objectClass': ["inetOrgPerson", "organizationalPerson", "person"],
            'carLicense': barcode,
            'cn': str(random_id),
            'uid': "geld-" + str(random_id),
            'sn': str(random_id),
        }
        con = Users.get_ldap_instance()
        con.add_s(dn, modlist.addModlist(mods))
        return Users.get_by_id_card(barcode)

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
        try:
            con = Users.get_ldap_instance()
            con.delete_s(user['path'])
        except Exception as e:
            print("Error: " + str(e))
            exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=4)

    @staticmethod
    def save(user):
        changes = {}
        for key, ldap_mapping in Users.fields.items():
            new_value = None

            if key in user:
                new_value = user[key]

            if new_value is not None and "save" in ldap_mapping:
                save_function = ldap_mapping["save"]

                if callable(save_function):
                    new_value = save_function(new_value)

            if "_reference" in user and new_value != user["_reference"][key]:
                changes[key] = (user["_reference"][key], new_value)

        if not changes:
            return
        logger.info("LDAP change %s: %s", user["name"], changes)
        if config.NO_CHANGES:
            logger.info("Ignoring because config.NO_CHANGES")
            return
        for key, change in changes.items():
            old, new = change
            # logger.debug("User %s %s: changing %s (%s) from '%s' to '%s'" % (
            ldap_mapping = Users.fields[key]
            #    user["id"], user['name'], key, meta['ldap_field'], str(old),
            #    str(new)))
            try:
                Users.set_value(user, ldap_mapping["ldap_field"], new)
                user["_reference"][key] = new
            except Exception as e:
                print("LDAP error:", e)
