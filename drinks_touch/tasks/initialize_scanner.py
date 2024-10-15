from time import sleep

from tasks.base import BaseTask


class InitializeScannerTask(BaseTask):
    label = "Initialisiere Barcode-Scanner"

    def run(self):
        for i in range(100):
            if self.sig_killed:
                break
            self.output += f"Simulate Doing Stuff {i}\n"
            sleep(0.03)
        raise ValueError("Scanner nicht gefunden")
