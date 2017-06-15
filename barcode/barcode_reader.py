import sys
import keyboard

from env import is_pi

def run(worker):
    global last_barcode
    if not is_pi():
        print "---------"
        print "Enter EAN here to simulate scanned barcode!"
        while True:
            worker.on_barcode(sys.stdin.readline().strip())

    while True:
        for barcode in keyboard.get_typed_strings(keyboard.record()):
            worker.on_barcode(barcode)
