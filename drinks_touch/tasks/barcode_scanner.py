import select
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
    thread = None

    def run(self):
        if (
            InitializeBarcodeScannerTask.thread
            and InitializeBarcodeScannerTask.thread.is_alive()
        ):
            self.output += "Barcode-Scanner läuft bereits. Starte neu...\n"
            BarcodeWorker.kill()
            InitializeBarcodeScannerTask.thread.join()

        InitializeBarcodeScannerTask.thread = threading.Thread(target=BarcodeWorker.run)
        InitializeBarcodeScannerTask.thread.daemon = True
        InitializeBarcodeScannerTask.thread.start()


class BarcodeWorker:
    killed = False

    @staticmethod
    def run():
        BarcodeWorker.killed = False
        if is_pi():
            BarcodeWorker._read_from_serial()
        else:
            BarcodeWorker._read_from_stdin()

    @staticmethod
    def kill():
        BarcodeWorker.killed = True

    @staticmethod
    def on_barcode(barcode):
        from screens.screen_manager import ScreenManager

        screen = ScreenManager.get_instance().get_active()

        if hasattr(screen, "on_barcode"):
            screen.on_barcode(barcode)

    @staticmethod
    def _read_from_stdin():
        """
        Read from stdin to simulate barcode scanner input
        """
        logger.info("Enter EAN here to simulate scanned barcode!")

        while not BarcodeWorker.killed:
            try:
                if select.select(
                    [
                        sys.stdin,
                    ],
                    [],
                    [],
                    2.0,
                )[0]:
                    line = sys.stdin.readline().strip().upper()
                    BarcodeWorker.on_barcode(line)
                else:
                    logger.debug("No input available")
            except Exception:
                logger.exception("Caught exception in barcode handler...")

    @staticmethod
    def _read_from_serial():
        with serial.Serial(config.SCANNER_DEVICE_PATH, baudrate=115200) as s:
            while not BarcodeWorker.killed:
                keyboard_input = s.read_until(b"\r").decode("utf-8")[:-1]
                if keyboard_input is None:
                    continue
                scanned_barcode = keyboard_input
                BarcodeWorker.on_barcode(scanned_barcode.upper())
