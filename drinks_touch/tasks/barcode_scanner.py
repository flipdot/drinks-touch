import threading

from screens.screen_manager import ScreenManager
from tasks.base import BaseTask

import serial
import logging

import config
from env import is_pi
from tasks.run_cmd import CheckoutAndRestartTask

logger = logging.getLogger(__name__)


class InitializeBarcodeScannerTask(BaseTask):
    LABEL = "Initialisiere Barcode-Scanner"
    ON_STARTUP = True
    thread = None

    def run(self):
        if (
            InitializeBarcodeScannerTask.thread
            and InitializeBarcodeScannerTask.thread.is_alive()
        ):
            self.logger.info("Barcode-Scanner läuft bereits. Starte neu...")
            BarcodeWorker.kill()
            InitializeBarcodeScannerTask.thread.join()

        InitializeBarcodeScannerTask.thread = threading.Thread(target=BarcodeWorker.run)
        InitializeBarcodeScannerTask.thread.daemon = True
        InitializeBarcodeScannerTask.thread.start()
        self.logger.info("Bereit. Scan doch mal was!")

    def on_barcode(self, barcode):
        self.logger.info(f"Barcode gescannt: {barcode}")


class BarcodeWorker:
    killed = False

    @staticmethod
    def run():
        BarcodeWorker.killed = False
        if is_pi():
            BarcodeWorker._read_from_serial()

    @staticmethod
    def kill():
        BarcodeWorker.killed = True

    @staticmethod
    def on_barcode(barcode):
        screen = ScreenManager.instance.get_active()

        if barcode == "RESTART":
            from screens.tasks_screen import TasksScreen

            screen.goto(TasksScreen(screen.screen, [CheckoutAndRestartTask("master")]))
            return

        screen.on_barcode(barcode)

    @staticmethod
    def _read_from_serial():
        with serial.Serial(config.SCANNER_DEVICE_PATH, baudrate=115200, timeout=5) as s:
            buffer = b""
            while not BarcodeWorker.killed:
                buffer += s.read_until(b"\r")
                if buffer.endswith(b"\r"):
                    scanned_barcode = buffer.decode("utf-8").strip()
                    buffer = b""
                    BarcodeWorker.on_barcode(scanned_barcode.upper())
