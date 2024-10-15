import threading
import time
from random import random

from elements.progress_bar import ProgressBar


class BaseTask:
    def __init__(self):
        self.progress_bar: ProgressBar | None = None
        self.lock = threading.Lock()
        self._output = ""
        self._progress = None
        self.finished = False
        self.status = None
        self.sig_killed = False

        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True

    @property
    def label(self):
        return self.__class__.__name__

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value: float):
        assert 0 <= value <= 1, "Progress must be between 0 and 1"
        self._progress = value
        if self.progress_bar is not None:
            self.progress_bar.percent = value

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value: str):
        self._output = value
        if self.progress_bar is not None:
            self.progress_bar.text = value

    def make_progress_bar(self, *args, **kwargs) -> ProgressBar:
        self.progress_bar = ProgressBar(
            *args, **kwargs, label=self.label, text=self.output
        )
        return self.progress_bar

    def start(self):
        self.thread.start()

    def run(self):
        for i in range(100):
            if self.sig_killed:
                break
            self.progress = i / 100
            self.output += f"Not implemented {i}%\n"
            time.sleep(0.1 * random())
        self._fail()

    def _success(self):
        if self.progress_bar is not None:
            self.progress_bar.success()
        self.finished = True
        self.status = 0

    def _fail(self, status=-1):
        if self.progress_bar is not None:
            self.progress_bar.fail()
        self.finished = True
        self.status = -1

    def kill(self):
        self.sig_killed = True
        self.thread.join()
