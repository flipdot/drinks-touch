from elements import Label, Button
from inspect import getmembers, isclass
import tasks as tasks_module
from elements.vbox import VBox
from tasks.base import BaseTask
from .screen import Screen


def discover_tasks():
    return [
        Task
        for _, Task in getmembers(tasks_module, isclass)
        if issubclass(Task, BaseTask) and Task.ON_STARTUP
    ]


class TasksScreen(Screen):
    def __init__(self, screen, tasks: list[BaseTask] | None = None, box_height=90):
        super().__init__(screen)
        self.finished = False

        if tasks:
            self.tasks = tasks
        else:
            self.tasks = [Task() for Task in discover_tasks()]

        progress_bars = [
            task.make_progress_bar(box_height=box_height, width=470)
            for task in self.tasks
        ]

        self.objects = [
            Label(
                text="Initialisierung...",
                pos=(5, 5),
            ),
            VBox(progress_bars, gap=10, pos=(5, 80)),
            Button(
                text="Abbrechen / Zurück",
                pos=(5, 795),
                align_bottom=True,
                on_click=self.cancel_tasks,
            ),
        ]

    def on_start(self, *args, **kwargs):
        self.finished = False
        for task in self.tasks:
            task.start()

    def render(self, *args, **kwargs):
        super(TasksScreen, self).render(*args, **kwargs)
        self.check_task_completion()

    @property
    def all_tasks_finished(self):
        return all(task.finished for task in self.tasks)

    def check_task_completion(self):
        if not self.finished and self.all_tasks_finished:
            # TODO: Progress object doesn't work well with navigating back and forth
            #  / reusing an old screen instance
            # self.objects.append(
            #     Progress(
            #         pos=(475, 795),
            #         speed=1 / 10,
            #         align_right=True,
            #         align_bottom=True,
            #         on_elapsed=self.back,
            #     )
            # )
            self.finished = True

    def cancel_tasks(self):
        if self.all_tasks_finished:
            self.back()
        for task in self.tasks:
            task.kill()

    def on_barcode(self, barcode):
        for task in self.tasks:
            task.on_barcode(barcode)
