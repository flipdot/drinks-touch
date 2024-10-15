import sys

import serial
import logging

import config
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

    with serial.Serial(config.SCANNER_DEVICE_PATH, baudrate=115200) as s:

        while True:
            keyboard_input = s.read_until(b"\r").decode("utf-8")[:-1]
            if keyboard_input is None:
                continue
            scanned_barcode = keyboard_input
            worker.on_barcode(scanned_barcode.upper())
