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
    BOX_HEIGHT = 90

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
                    pos=(10, 100 + i * (SyncScreen.BOX_HEIGHT + 80)),
                    box_height=SyncScreen.BOX_HEIGHT,
                )
            )
            task.start()

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
                    self.screen,
                    pos=(440, 760),
                    speed=1 / 5,
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
