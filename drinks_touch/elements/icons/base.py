import pygame

from config import COLORS
from elements.base_elm import BaseElm


class BaseIcon(BaseElm):
    SIZE = 24
    COLOR = COLORS["infragelb"]

    def __init__(self, pos=None, width=None, height=None):
        super().__init__(None, pos=pos)
        self.width = width or self.SIZE
        self.height = height or self.SIZE

    def render(self, *args, **kwargs) -> pygame.Surface:
        assert self.pos is not None
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw(surface)
        return surface

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            (255, 0, 255),
            (self.width / 2, self.height / 2),
            self.width / 2,
        )
