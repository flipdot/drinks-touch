import json

import ldap
import ldap.modlist as modlist
import traceback
import random

from datetime import datetime

from database.storage import get_session
from sqlalchemy.sql import text
from env import is_pi

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
            "ldap_field": "seeAlso",
            "index": 0,
            "default": {
                "drink_notification": "instant", # instant, daily, weekly, never
                "last_drink_notification": 0,
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
    def get_all(prefix='', filters=[], include_temp=False):
        try:
            users = []
            ldap_users = Users.read_all_users_ldap(filters, include_temp)

            for ldap_user in ldap_users:
                name = ldap_user['uid'][0]

                if prefix != '' and name.lower().startswith(prefix.lower()) == False:
                    continue

                user = {}
                for key, meta in Users.fields.iteritems():
                    try:
                        value = ldap_user[meta['ldap_field']]
                        if "index" in meta:
                            value = value[meta["index"]]
                        if "load" in meta:
                            value = meta['load'](value)
                        if value == None and "default" in meta:
                            value = meta["default"]
                        user[key] = value
                    except:
                        if 'default' in meta:
                            user[key] = meta['default']
                        else:
                            raise

                user["_reference"] = {}
                for key, meta in Users.fields.iteritems():
                    value = user[key]
                    if "save" in meta:
                        value = meta["save"](value)
                    user["_reference"][key] = value

                if user['id_card']:
                    user['id_card'] = user['id_card'].upper()
                Users.save(user)

                users.append(user)

            return users
        except Exception as e:
            if not is_pi():
                print("ldap fail: ", e)
                print(traceback.format_exc())
                print("falling back to test data")
                return filter(lambda u: prefix == '' or
                    u['name'].lower().startswith(prefix.lower()),
                    [{"name": "foo", "id":"1", "id_card": None},
                    {"name": "bar", "id":"2", "id_card": "idcard2"},
                    {"name": "Baz", "id":"3", "id_card": "idcard"},
                    {"name": "Daz", "id":"3", "id_card": "idcard"}])
            else:
                raise

    @staticmethod
    def get_ldap_instance():
        dn = "cn=admin,dc=flipdot,dc=org"
        pw = ''
        with  open('ldap_pw', 'r') as ldap_pw:
            pw = ldap_pw.read().replace('\n', '')
        
        con = ldap.initialize('ldap://rail.fd')
        con.simple_bind_s( dn, pw )
        return con

    @staticmethod
    def read_all_users_ldap(filters=[], include_temp=False):
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
            ldap_res.extend(con.search_s(temp_dn, ldap.SCOPE_SUBTREE, filter_str, attrs))

        users = []
        for path, user in ldap_res:
            if not 'uidNumber' in user:
                user['uidNumber'] = user['uid']
            if not 'carLicense' in user:
                user['carLicense'] = [None]
            user['path'] = path
            users.append(user)

        con.unbind()
        return users
        
    @staticmethod
    def get_balance(user_id, session=get_session()):
        sql = text("""
                SELECT user_id, count(*) as amount
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
                SELECT user_id, sum(amount) as amount
                FROM rechargeevent
                WHERE user_id = :user_id
                GROUP BY user_id
            """)
        print sql, user_id
        row = session.connection().execute(sql, user_id=user_id).fetchone()
        if not row:
            credit = 0
        else:
            credit = row.amount

        return credit - cost

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
    def get_by_id_card(ean):
        all = Users.get_all(filters=['carLicense='+ean], include_temp=True)
        by_card = dict([ (u['id_card'], u) for u in all if u['id_card'] ])
        if ean in by_card:
            return by_card[ean]
        return None

    @staticmethod
    def id_to_ean(id):
        return "FDT" + str(id)

    @staticmethod
    def create_temp_user():
        id = 30000 + random.randint(1,2000)
        while Users.get_by_id_card(Users.id_to_ean(id)):
            id += 1
        
        barcode = Users.id_to_ean(id)
        dn = "cn=" + str(id) + ",ou=temp_members,dc=flipdot,dc=org"
        mods = {
            'objectClass':  ["inetOrgPerson", "organizationalPerson", "person"],
            'carLicense':   barcode,
            'cn':           str(id),
            'uid':          "geld-"+str(id),
            'sn':           str(id),
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
            print "deleting user " + str(user['id']) + " because they are broke"
            Users.delete(user)
    
    @staticmethod
    def delete(user):
        try:
            con = Users.get_ldap_instance()
            con.delete_s(user['path'])
        except Exception as e:
            print "Error: " + str(e)
            traceback.print_tb(limit=4)

    @staticmethod
    def save(user):
        changes = {}
        for key, meta in Users.fields.iteritems():
            new_value = user[key]
            if "save" in meta:
                new_value = meta["save"](new_value)
            if new_value != user["_reference"][key]:
                changes[key] = (user["_reference"][key], new_value)

        if changes:
            for key, change in changes.iteritems():
                old, new = change
                meta = Users.fields[key]
                print("User %s %s: changing %s from '%s' to '%s'" % (
                    user["id"], user['name'], key, str(old), str(new)))
                try:
                    Users.set_value(user, meta["ldap_field"], new)
                    user["_reference"][key] = new
                except Exception as e:
                    print "LDAP error:", e
