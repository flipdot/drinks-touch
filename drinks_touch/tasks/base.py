import threading
import time
from random import random

from elements.progress_bar import ProgressBar
import logging

logger = logging.getLogger(__name__)


class LogHandler(logging.Handler):
    def __init__(self, task):
        super(LogHandler, self).__init__()
        self.task = task
        self.output = ""

    def emit(self, record):
        self.output += self.format(record) + "\n"
        if self.task.progress_bar is not None:
            self.task.progress_bar.text = self.output


class BaseTask:
    def __init__(self):
        self.progress_bar: ProgressBar | None = None
        self.lock = threading.Lock()
        self._output = ""
        self._progress = None
        self.finished = False
        self.status = None
        self.sig_killed = False

        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True

        self.logger = logging.getLogger(self.__class__.__name__)

        handler = LogHandler(self)
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)

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

    def make_progress_bar(self, *args, **kwargs) -> ProgressBar:
        self.progress_bar = ProgressBar(*args, **kwargs, label=self.label, text=None)
        return self.progress_bar

    def start(self):
        self.thread.start()

    def _run(self):
        try:
            self.run()
        except Exception as e:
            logger.exception(f"Error in task {self.label}")
            self.logger.error(f"Error: {e}")
            self._fail()
        else:
            self._success()

    def run(self):
        for i in range(100):
            if self.sig_killed:
                break
            self.progress = i / 100
            self.logger.info(f"Not implemented {i}%")
            time.sleep(0.1 * random())
        raise NotImplementedError(f"Override tasks.{self.__class__.__name__}.run()")

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

    def on_barcode(self, barcode):
        pass
