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

            barcode = replace_key_code(replace_key_code, {
                "?": "_",
                "_": "?"
            })

            worker.on_barcode(barcode)
