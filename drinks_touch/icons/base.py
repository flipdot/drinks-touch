import pygame


class BaseIcon:
    SIZE = 24
    COLOR = (246, 198, 0)

    def __init__(self):
        self.size = self.SIZE

    def render(self):
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.draw(surface)
        return surface

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            (255, 0, 255),
            (self.size / 2, self.size / 2),
            self.size / 2,
        )
