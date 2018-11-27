import logging

from database.models.ldapUser import LdapUser
from database.storage import get_session, init_db
from users.users import Users


def main():
    users = Users.get_all(include_temp=True)

    init_db()
    session = get_session()

    for user in users:
        ldapName = user["name"]
        ldapUser = LdapUser(
            ldapId=user["id"],
            name=ldapName,
            id_card=user["id_card"],
            path=user["path"],
            is_card=ldapName.startswith("geld")
        )

        session.add(ldapUser)

    session.commit()


main()
