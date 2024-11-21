import pygame

from config import Color
from .base import BaseIcon


class SvgIcon(BaseIcon):

    def __init__(
        self, path, pos=None, color: Color | None = None, width=None, height=None
    ):
        """
        If one of width or height is set and the other is None, the other
        will be calculated to keep the aspect ratio.
        """
        super().__init__(pos=pos)
        self.path = path
        image = pygame.image.load(self.path).convert_alpha()
        if color:
            image.fill(color.value, special_flags=pygame.BLEND_RGBA_MIN)

        if width and height is None:
            aspect_ratio = image.get_width() / image.get_height()
            height = int(width / aspect_ratio)
        elif height and width is None:
            aspect_ratio = image.get_height() / image.get_width()
            width = int(height / aspect_ratio)

        if width and height:
            self.image = pygame.transform.scale(image, (width, height))
            self.width = width
            self.height = height
        else:
            self.image = image

    def draw(self, surface):
        surface.blit(self.image, (0, 0))
