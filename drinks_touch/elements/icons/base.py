import pygame

from config import Color
from elements.base_elm import BaseElm


class BaseIcon(BaseElm):
    SIZE = 24
    COLOR = Color.PRIMARY

    def __init__(self, pos=None, width=None, height=None, visible=True):
        super().__init__(pos=pos)
        self.width = width or self.SIZE
        self.height = height or self.SIZE
        self.visible = visible

    def render(self, *args, **kwargs) -> pygame.Surface | None:
        if not self.visible:
            return None
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
