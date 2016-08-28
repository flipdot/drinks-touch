import ldap

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

        with  open('ldap_pw', 'r') as ldap_pw
            pw = ldap_pw.read()
        
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
        
