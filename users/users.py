import ldap
import traceback

from database.storage import get_session
from sqlalchemy.sql import text
from env import is_pi

class Users(object):
    active_user = None

    def __init__(self):
        pass

    @staticmethod
    def get_all(prefix=''):
        try:
            users = []
            ldap_users = Users.read_all_users_ldap()

            for ldap_user in ldap_users:
                name = ldap_user['uid'][0]

                if prefix != '' and name.lower().startswith(prefix.lower()) == False:
                    continue

                users.append({
                    "path": ldap_user['path'],
                    "name": name,
                    "id": ldap_user['uidNumber'][0],
                    "id_card": ldap_user['carLicense'][0],
                })
            return users
        except Exception as e:
            if not is_pi():
                print("ldap fail: ", e)
                print(traceback.format_exc())
                print("falling back to test data")
                return filter(lambda u: prefix == '' or
                    u['name'].lower().startswith(prefix.lower()),
                    [{"name": "foo", "id":"1", "id_card": ""},
                    {"name": "bar", "id":"2", "id_card": ""},
                    {"name": "baz", "id":"3", "id_card": ""}])
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
    def read_all_users_ldap():
        base_dn = 'ou=members,dc=flipdot,dc=org'
        filter = '(objectclass=person)'
        attrs = ['uid', 'uidNumber', 'carLicense']
        
        con = Users.get_ldap_instance()
        
        users = []
        for path, user in con.search_s( base_dn, ldap.SCOPE_SUBTREE, filter, attrs ):
            if not 'uidNumber' in user:
                user['uidNumber'] = user['uid']
            if not 'carLicense' in user:
                user['carLicense'] = [None]
            user['path'] = path
            users.append(user)

        con.unbind()
        return users
        
    @staticmethod
    def get_balance(user_id):
        session = get_session()

        sql = text("""
                SELECT user_id, count(*) as amount
                FROM scanevent
                WHERE user_id = :user_id
                GROUP BY user_id
            """)
        row = session.connection().execute(sql, user_id=user_id).fetchone()
        if not row:
            return None

        cost = row.amount

        sql = text("""
                SELECT user_id, sum(amount) as amount
                FROM rechargeevent
                WHERE user_id = :user_id
                GROUP BY user_id
            """)
        row = session.connection().execute(sql, user_id=user_id).fetchone()
        if not row:
            return cost * -1

        credit = row.amount        

        return credit - cost

    @staticmethod
    def set_id_card(user_path, ean):
        con = Users.get_ldap_instance()
        add_pass = [(ldap.MOD_REPLACE, 'carLicense', [ean])]
        con.modify_s(user_path,add_pass)