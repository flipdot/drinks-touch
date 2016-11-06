import pygame
import math

from .base_elm import BaseElm

class Progress(BaseElm):
    def __init__(self, screen, **kwargs):
        self.size = kwargs.get('size', 30)
        self.color = kwargs.get('color', (246, 198, 0))
        self.box = None
        self.value = 0
        self.tick = kwargs.get('tick', self.default_tick)
        self.speed = self.calc_speed(kwargs.get('speed', 8))
        self.on_elapsed = kwargs.get('on_elapsed', None)

        pos = kwargs.get('pos', (0, 0))
        super(Progress, self).__init__(screen, pos, self.size, -1)
        top = self.pos[0] - self.size/2
        left = self.pos[1] - self.size/2
        width = self.size
        height = self.size

        self.box = (
            top, left,
            width, height
        )

    def calc_speed(self, value):
        return value / 1000.0

    def default_tick(self, value):
        if value >= 1 and self.on_elapsed:
            self.on_elapsed()
        return value + self.speed

    def render(self):
        if self.tick is not None:
            self.value = self.tick(self.value)

        pygame.draw.arc(
            self.screen,
            self.color,
            self.box,
            0.5*math.pi - self.value * math.pi * 2, 0.5*math.pi,
            int(self.size/5)
        )
