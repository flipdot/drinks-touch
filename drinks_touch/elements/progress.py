import math

from config import COLORS
from .base_elm import BaseElm

import contextlib

with contextlib.redirect_stdout(None):
    import pygame


class Progress(BaseElm):
    def __init__(self, pos=None, *args, **kwargs):
        self.size = kwargs.get("size", 50)
        self.color = kwargs.get("color", COLORS["infragelb"])
        self.tick = kwargs.get("tick", self.__default_tick)
        self.speed = kwargs.get("speed", 1 / 4.0)  # 4 secs
        self.on_elapsed = kwargs.get("on_elapsed", None)
        self.value = 0
        self.is_running = False

        super(Progress, self).__init__(pos, self.size, self.size, *args, **kwargs)
        self.start()

    def start(self):
        self.value = 0
        self.is_running = True

    def stop(self):
        self.is_running = False

    def __default_tick(self, old_value, dt):
        if self.is_running and old_value >= 1:
            self.stop()
            if self.on_elapsed:
                self.on_elapsed()

        if self.is_running:
            return old_value + self.speed * dt
        else:
            return old_value

    def render(self, dt) -> pygame.Surface:
        if self.tick is not None:
            self.value = self.tick(self.value, dt)

        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        if self.is_running:
            extra_rounds = 0.75
            start = 0.5 * math.pi + self.value * math.pi * extra_rounds * 2
            end = start + self.value * 2 * math.pi
            pygame.draw.arc(
                surface,
                self.color,
                (0, 0, self.width, self.height),
                start,
                end,
                int(self.size / 5),
            )
        return surface
