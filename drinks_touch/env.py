import os


def is_pi():
    return os.environ.get("ENV") == "PI"
