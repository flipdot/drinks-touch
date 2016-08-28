import ldap

from database.storage import get_session
from sqlalchemy.sql import text

class Users(object):
    active_user = None

    def __init__(self):
        pass

    @staticmethod
    def get_all(filter=''):
        users = []
        ldap_users = Users.read_all_users_ldap()

        for ldap_user in ldap_users:
            name = ldap_user['uid'][0]

            if filter != '' and name.lower().startswith(filter.lower()) == False:
                continue

            users.append({
                "name": name,
                "id": ldap_user['uidNumber'][0]
            })

        return users

    @staticmethod
    def read_all_users_ldap():
        dn = "cn=admin,dc=flipdot,dc=org"
        pw = ''

        with  open('ldap_pw', 'r') as ldap_pw:
            pw = ldap_pw.read().replace('\n', '')

        base_dn = 'ou=members,dc=flipdot,dc=org'
        filter = '(objectclass=person)'
        attrs = ['uid', 'uidNumber']

        con = ldap.initialize('ldap://rail.fd')
        con.simple_bind_s( dn, pw )
        
        users = []
        for path, user in con.search_s( base_dn, ldap.SCOPE_SUBTREE, filter, attrs ):
            if not 'uidNumber' in user:
                user['uidNumber'] = user['uid']
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