import threading

from tasks.base import BaseTask

import sys

import serial
import logging

import config
from env import is_pi

logger = logging.getLogger(__name__)


class InitializeBarcodeScannerTask(BaseTask):
    label = "Initialisiere Barcode-Scanner"

    def __init__(self):
        super().__init__()
        self.barcode_thread = threading.Thread(target=run_barcode_thread)
        self.barcode_thread.daemon = True

    def run(self):
        self.barcode_thread.start()


def on_barcode(barcode):
    from screens.screen_manager import ScreenManager

    screen = ScreenManager.get_instance().get_active()

    if hasattr(screen, "on_barcode"):
        screen.on_barcode(barcode)


def run_barcode_thread():
    if is_pi():
        read_from_serial(callback=on_barcode)
    else:
        read_from_stdin(callback=on_barcode)


def read_from_stdin(callback):
    """
    Read from stdin to simulate barcode scanner input
    """
    logger.info("Enter EAN here to simulate scanned barcode!")

    while True:
        try:
            callback(sys.stdin.readline().strip().upper())
        except Exception:
            logger.exception("Caught exception in barcode handler...")


def read_from_serial(callback):
    with serial.Serial(config.SCANNER_DEVICE_PATH, baudrate=115200) as s:
        while True:
            keyboard_input = s.read_until(b"\r").decode("utf-8")[:-1]
            if keyboard_input is None:
                continue
            scanned_barcode = keyboard_input
            callback(scanned_barcode.upper())
