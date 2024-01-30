import sys

import serial
import logging

from env import is_pi

logger = logging.getLogger(__name__)


def run(worker):
    if not is_pi():
        logger.info("Enter EAN here to simulate scanned barcode!")

        while True:
            try:
                worker.on_barcode(sys.stdin.readline().strip().upper())
            except Exception:
                logger.exception("Caught exception in barcode handler...")

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
    with serial.Serial("/dev/ttyACM0", baudrate=115200) as s:

        while True:
            keyboard_input = s.read_until(b"\r").decode("utf-8")[:-1]
            print("input '{}'".format(keyboard_input))
            if keyboard_input is None:
                continue
            scanned_barcode = replace_key_code(keyboard_input, {
                "?": "_",
                "_": "?"
            })
            worker.on_barcode(scanned_barcode.upper())
