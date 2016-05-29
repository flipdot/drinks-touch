import ldap

class Users(object):
    active_user = None

    def __init__(self):
        pass

    @staticmethod
    def get_all(filter):
        users = []
        ldap_users = Users.read_all_users_ldap()

        for ldap_user in ldap_users:
            name = ldap_user['uid'][0]

            if name.lower().startswith(filter.lower()) == False:
                continue

            users.append({
                "name": name,
                "id": ldap_user['uidNumber'][0],
                "drinks": [
                    {
                        "name": "Mio Mate",
                        "count": 6
                    },
                    {
                        "name": "Krombacher",
                        "count": 3
                    },
                    {
                        "name": "Club Mate",
                        "count": 2
                    }                   
                ]
            })

        return users
    
    @staticmethod
    def set_active(user):
        Users.active_user = user

    @staticmethod
    def reset_active():
        Users.set_active(None)

    @staticmethod
    def get_active_user():
        return Users.active_user

    @staticmethod
    def read_all_users_ldap():
        dn = "cn=admin,dc=flipdot,dc=org"
        pw = "password"
        
        base_dn = 'ou=members,dc=flipdot,dc=org'
        filter = '(objectclass=person)'
        attrs = ['uid', 'uidNumber']


        con = ldap.initialize('ldap://rail.fd')
        con.simple_bind_s( dn, pw )
        
        users = []
        for path, user in con.search_s( base_dn, ldap.SCOPE_SUBTREE, filter, attrs ):
            users.append(user)

        con.unbind()
        return users
        