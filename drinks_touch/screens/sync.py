from elements import Label, Progress, Button
from inspect import getmembers, isclass
import tasks
from elements.base_elm import BaseElm
from elements.vbox import VBox
from tasks.base import BaseTask
from .screen import Screen


def discover_tasks():
    return [
        Task for _, Task in getmembers(tasks, isclass) if issubclass(Task, BaseTask)
    ]


class SyncScreen(Screen):
    def __init__(self, screen):
        super(SyncScreen, self).__init__(screen)
        self.finished = False

        self.tasks = [Task() for Task in discover_tasks()]

        progress_bars = [
            task.make_progress_bar(box_height=90, width=470) for task in self.tasks
        ]

        for task in self.tasks:
            task.start()

        self.objects: list[BaseElm] = [
            Label(
                text="Initialisierung...",
                pos=(5, 5),
            ),
            VBox(self.screen, progress_bars, gap=10, pos=(5, 80)),
            Button(
                text="Abbrechen",
                pos=(5, 795),
                align_bottom=True,
                click_func=self.cancel_tasks,
            ),
        ]

    def render(self, *args, **kwargs):
        super(SyncScreen, self).render(*args, **kwargs)
        self.check_task_completion()

    @property
    def all_tasks_finished(self):
        return all(task.finished for task in self.tasks)

    def check_task_completion(self):
        if not self.finished and self.all_tasks_finished:
            self.objects.append(
                Progress(
                    pos=(475, 795),
                    speed=1 / 10,
                    align_right=True,
                    align_bottom=True,
                    on_elapsed=self.time_elapsed,
                )
            )
            self.finished = True

    def cancel_tasks(self):
        if self.all_tasks_finished:
            self.time_elapsed()
        for task in self.tasks:
            task.kill()

    def time_elapsed(self):
        from screens.screen_manager import ScreenManager

        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()

    def on_barcode(self, barcode):
        for task in self.tasks:
            task.on_barcode(barcode)
