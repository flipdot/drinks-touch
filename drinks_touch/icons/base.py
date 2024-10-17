import pygame


class BaseIcon:
    SIZE = 24
    COLOR = (246, 198, 0)

    def __init__(self, width=None, height=None):
        self.width = width or self.SIZE
        self.height = height or self.SIZE

    def render(self):
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
