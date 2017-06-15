import io
import subprocess
import sys
import os
import time
import threading

import pprint

import keyboard

from env import is_pi

def run(worker):
    global last_barcode
    if not is_pi():
        print "---------"
        print "Enter EAN here to simulate scanned barcode!"
        while True:
            worker.on_barcode(sys.stdin.readline().strip())

    global keyboard_buffer
    keyboard_buffer = ''

    def apply_code_fix(char):
        if char == '?':
            return '_'

        if char == '_':
            return '?'

        return char

    def keyboard_up_callback(event):
        global keyboard_buffer

        c = apply_code_fix(event.name)
        if c == 'tab':
            print "barcode: ", keyboard_buffer
            worker.on_barcode(keyboard_buffer)
            keyboard_buffer = ''
        elif c == 'shift':
            # we may ignore the shift
            # at the beginning of a barcode
            pass
        else:
            keyboard_buffer += c

    keyboard.on_release(keyboard_up_callback)