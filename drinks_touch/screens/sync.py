from elements import Label, Progress, Button
from inspect import getmembers, isclass
import tasks
from elements.base_elm import BaseElm
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

        self.objects: list[BaseElm] = [
            Label(
                self.screen,
                text="Initialisierung...",
                pos=(10, 25),
            ),
            Button(
                self.screen,
                text="Abbrechen",
                pos=(20, 750),
                click_func=self.cancel_tasks,
            ),
        ]

        for i, task in enumerate(self.tasks):
            self.objects.append(
                task.make_progress_bar(
                    self.screen,
                    pos=(10, 100 + i * 135),
                    box_height=60,
                )
            )
            task.start()

    def render(self, *args, **kwargs):
        super(SyncScreen, self).render(*args, **kwargs)
        self.check_task_completion()

    def check_task_completion(self):
        if not self.finished and all(task.finished for task in self.tasks):
            self.objects.append(
                Progress(
                    self.screen,
                    pos=(440, 760),
                    speed=1 / 5,
                    on_elapsed=self.time_elapsed,
                )
            )
            self.finished = True

    def cancel_tasks(self):
        for task in self.tasks:
            task.kill()

    def time_elapsed(self):
        from screens.screen_manager import ScreenManager

        screen_manager = ScreenManager.get_instance()
        screen_manager.set_default()
