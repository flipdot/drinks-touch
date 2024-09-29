#!/usr/bin/env python3

import sys

import socket
from PIL import Image

host = "192.168.3.36"
# host='127.0.0.1'
port = 2323

w = 48
h = 20


def usage():
    print("flipdots.py IMAGEFILE")


def create_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return s
    except socket.error:
        print("Failed to create socket")
        sys.exit(1)


def send_bytes(byte_socket, msg):
    byte_socket.sendto(msg, (host, port))


def send_frame(s, i):
    i.thumbnail((w, h))
    i = i.convert("1").transpose(Image.ROTATE_90)
    send_bytes(s, i.tobytes())
    # i.show()


def main(argv):
    if len(argv) != 1:
        usage()
        sys.exit()

    f = argv[0]
    s = create_socket()
    i = Image.open(f)

    send_frame(s, i)
    while True:
        try:
            i.seek(i.tell() + 1)
            send_frame(s, i)
        except EOFError:
            # DEBUG
            # print("No more frames to send")
            break


if __name__ == "__main__":
    main(sys.argv[1:])
