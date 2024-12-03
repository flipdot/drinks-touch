import math

import pygame

from .base import BaseIcon


class RefreshIcon(BaseIcon):
    SIZE = 36

    def draw(self, surface):
        pygame.draw.arc(
            surface,
            self.COLOR.value,
            (0, 0, self.width, self.height),
            math.pi * 0.2,
            math.pi * 0.8,
            6,
        )

        pygame.draw.arc(
            surface,
            self.COLOR.value,
            (0, 0, self.width, self.height),
            math.pi * 1.2,
            math.pi * 1.8,
            6,
        )

        pygame.draw.polygon(
            surface,
            self.COLOR.value,
            [
                (self.width * 0.6, self.height * 0.4),
                (self.width * 0.95, self.height * 0.4),
                (self.width * 0.95, self.height * 0.05),
            ],
        )

        pygame.draw.polygon(
            surface,
            self.COLOR.value,
            [
                (self.width * 0.4, self.height * 0.6),
                (self.width * 0.05, self.height * 0.6),
                (self.width * 0.05, self.height * 0.95),
            ],
        )
