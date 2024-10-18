import math

import pygame

from icons.base import BaseIcon


class RefreshIcon(BaseIcon):
    SIZE = 36

    def draw(self, surface):
        pygame.draw.arc(
            surface,
            self.COLOR,
            (0, 0, self.size, self.size),
            math.pi * 0.2,
            math.pi * 0.8,
            6,
        )

        pygame.draw.arc(
            surface,
            self.COLOR,
            (0, 0, self.size, self.size),
            math.pi * 1.2,
            math.pi * 1.8,
            6,
        )

        pygame.draw.polygon(
            surface,
            self.COLOR,
            [
                (self.size * 0.6, self.size * 0.4),
                (self.size * 0.95, self.size * 0.4),
                (self.size * 0.95, self.size * 0.05),
            ],
        )

        pygame.draw.polygon(
            surface,
            self.COLOR,
            [
                (self.size * 0.4, self.size * 0.6),
                (self.size * 0.05, self.size * 0.6),
                (self.size * 0.05, self.size * 0.95),
            ],
        )
