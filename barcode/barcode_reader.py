import sys
import keyboard
import logging

from env import is_pi

def run(worker):
    global last_barcode
    if not is_pi():
        print "---------"
        print "Enter EAN here to simulate scanned barcode!"
        while True:
            try:
                worker.on_barcode(sys.stdin.readline().strip().upper())
            except Exception:
                logging.exception("Caught exception in barcode handler...")

    def replace_key_code(barcode, replacements):

        indexes_per_replacement = {}

        for source in replacements:
            indexes = []

            i = 0
            while True:
                try:
                    pos = barcode.index(source, i)
                    indexes.append(pos)
                    i = i + 1
                except ValueError:
                    break

            indexes_per_replacement[source] = indexes

        for source in indexes_per_replacement:
            indexes = indexes_per_replacement[source]
            target = replacements[source]

            for index in indexes:
                barcode = barcode[:index] + target + barcode[index + 1:]

        return barcode

    while True:
        for barcode in keyboard.get_typed_strings(keyboard.record(until="tab")):
            barcode = replace_key_code(barcode, {
                "?": "_",
                "_": "?"
            })

            worker.on_barcode(barcode.upper())
