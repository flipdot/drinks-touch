from database.models.ldapUser import LdapUser
from database.storage import get_session, init_db
from users.users import Users


def main():
    users = list(Users.get_all(include_temp=True))

    init_db()
    session = get_session()

    for user in users:
        ldap_name = user["name"]
        ldap_user = LdapUser(
            ldap_id=user["id"],
            name=ldap_name,
            id_card=user["id_card"],
            path=user["path"],
            is_card=ldap_name.startswith("geld"),
        )

        old = LdapUser.query.filter_by(ldapId=str(user["id"])).all()
        for old_user in old:
            session.delete(old_user)
        session.add(ldap_user)

    session.commit()


main()
