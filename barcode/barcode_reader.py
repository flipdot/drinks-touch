import io
import subprocess
import sys
import os
import time
import threading

import pprint

from env import is_pi

command = ['barcode_bin/barcode', '/dev/input/by-id/usb-GASIA_PS2toUSB_Adapter-event-kbd']
#command = ['barcode_bin/barcode', '/dev/input/by-id/usb-Logitech_USB_Receiver-if02-event-kbd']
devnull = open(os.devnull, 'wb')
last_barcode = time.time()

def run(worker):
    global last_barcode
    if not is_pi():
        print "---------"
        print "Enter EAN here to simulate scanned barcode!"
        while True:
            worker.on_barcode(sys.stdin.readline().strip())
    while True:
        #print "starting", command
        process = subprocess.Popen(
            command,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=devnull
        )
        last_barcode = time.time()
        reaper = threading.Thread(
            target=reap, args=(process,))
        reaper.start()
        buffer = ''
        for c in iter(lambda: process.stdout.read(1), ''):
            if c == '\n':
                last_barcode = time.time()
                print "barcode: ", buffer
                worker.on_barcode(buffer)
                buffer = ''
            else:
                buffer += c
        process.communicate()
        reaper.join()

def reap(process):
    global last_barcode
    while process.poll() == None:
        if abs(last_barcode - time.time()) > 30:
            #print "restarting barcode process"
            process.kill()
            break
        else:
            time.sleep(0.5)
