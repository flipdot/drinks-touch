import pygame

from elements.base_elm import BaseElm


class BaseIcon(BaseElm):
    SIZE = 24
    COLOR = (246, 198, 0)

    def __init__(self, screen, pos=None, width=None, height=None):
        super().__init__(screen, pos=pos)
        self.width = width or self.SIZE
        self.height = height or self.SIZE

    def render(self, *args, **kwargs):
        assert self.pos is not None
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw(surface)
        self.screen.blit(surface, self.pos)

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            (255, 0, 255),
            (self.width / 2, self.height / 2),
            self.width / 2,
        )
