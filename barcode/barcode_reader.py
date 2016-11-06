import io
import time
import subprocess
import sys
import os

import pprint

from env import is_pi

command = ['barcode_bin/barcode', '/dev/input/by-id/usb-GASIA_PS2toUSB_Adapter-event-kbd']
devnull = open(os.devnull, 'wb')

def run(worker):
    if not is_pi():
        print "---------"
        print "Enter EAN here to simulate scanned barcode!"
        while True:
            worker.on_barcode(sys.stdin.readline().strip())
    process = subprocess.Popen(
        command,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=devnull
    )
    buffer = ''
    for c in iter(lambda: process.stdout.read(1), ''):
        if c == '\n':
            worker.on_barcode(buffer)
            buffer = ''
        else:
            buffer += c
