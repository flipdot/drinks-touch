#!/usr/bin/env python3
import sys

from users.users import Users


def main():
    for user in Users.get_all():
        user['meta']['last_emailed'] = 0
        user['meta']['last_drink_notification'] = 0
        Users.save(user)


if __name__ == "__main__":
    sys.exit(main())
