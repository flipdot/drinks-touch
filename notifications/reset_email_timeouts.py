#!/usr/bin/env python2
# coding=utf8

import sys

import logging
import os

from users.users import Users

sys.path.append(os.path.dirname(__file__) + "/../")

logging.basicConfig()


def main(args):
    for user in Users.get_all():
        user['meta']['last_emailed'] = 0
        user['meta']['last_drink_notification'] = 0
        Users.save(user)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
