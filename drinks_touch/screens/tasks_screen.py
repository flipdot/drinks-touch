from elements import Label
from inspect import getmembers, isclass
import tasks as tasks_module
from elements.vbox import VBox
from tasks.base import BaseTask
from .screen import Screen
from .screen_manager import ScreenManager


def discover_tasks():
    return [
        Task
        for _, Task in getmembers(tasks_module, isclass)
        if issubclass(Task, BaseTask) and Task.ON_STARTUP
    ]


class TasksScreen(Screen):
    idle_timeout = 0

    def __init__(self, tasks: list[BaseTask] | None = None, box_height=None):
        super().__init__()
        self.finished = False

        if tasks:
            self.tasks = tasks
        else:
            self.tasks = [Task() for Task in discover_tasks()]

        if box_height is None:
            if len(self.tasks) == 1:
                box_height = 600
            else:
                box_height = 360 / len(self.tasks)
        self.box_height = box_height

    def on_start(self, *args, **kwargs):
        self.finished = False

        progress_bars = [
            task.make_progress_bar(box_height=self.box_height, width=470)
            for task in self.tasks
        ]

        self.objects = [
            Label(
                text="Initialisierung...",
                pos=(5, 5),
            ),
            VBox(progress_bars, gap=10, pos=(5, 80)),
        ]

        for task in self.tasks:
            task.start()

    def on_stop(self, *args, **kwargs):
        for task in self.tasks:
            task.kill()

    def render(self, *args, **kwargs):
        res = super(TasksScreen, self).render(*args, **kwargs)
        self.check_task_completion()
        return res

    @property
    def all_tasks_finished(self):
        return all(task.finished for task in self.tasks)

    def check_task_completion(self):
        if not self.finished and self.all_tasks_finished:
            self.idle_timeout = 5
            ScreenManager.instance.set_idle_timeout(self.idle_timeout)
            self.finished = True

    def on_barcode(self, barcode):
        for task in self.tasks:
            task.on_barcode(barcode)
