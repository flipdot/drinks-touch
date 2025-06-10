import math

import config
from .base_elm import BaseElm

import contextlib

with contextlib.redirect_stdout(None):
    import pygame


class Progress(BaseElm):
    def __init__(
        self,
        children: list["BaseElm"] | None = None,
        pos=None,
        size=50,
        color=config.Color.PRIMARY,
        speed=1 / 4.0,  # 4 secs
        on_elapsed=None,
        *args,
        **kwargs,
    ):
        self.size = size
        self.color = color
        self.speed = speed
        self.on_elapsed = on_elapsed
        self.value = 0
        self.is_running = False

        super(Progress, self).__init__(
            children, pos, self.size, self.size, *args, **kwargs
        )
        self.start()

    def calculate_hash(self):
        super_hash = super().calculate_hash()
        return hash(
            (
                super_hash,
                self.value,
                self.is_running,
                self.size,
                self.color,
            )
        )

    def start(self):
        self.value = 0
        self.is_running = True

    def stop(self):
        self.is_running = False

    def tick(self, dt: float):
        if not self.is_running:
            return
        if not self.on_elapsed:
            return

        self.value += self.speed * dt
        if self.value >= 1:
            self.on_elapsed()

    def _render(self, *args, **kwargs) -> pygame.Surface:
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        if self.is_running:
            extra_rounds = 0.75
            start = 0.5 * math.pi + self.value * math.pi * extra_rounds * 2
            end = start + self.value * 2 * math.pi
            pygame.draw.arc(
                surface,
                self.color.value,
                (0, 0, self.width, self.height),
                start,
                end,
                int(self.size / 5),
            )
        return surface
