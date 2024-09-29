#!/usr/bin/env python3
import sys

from users.users import Users


def main():
    for user in Users.get_all():
        user["lastEmailed"] = 0
        user["lastDrinkNotification"] = 0
        Users.save(user)


if __name__ == "__main__":
    main()
    sys.exit()
