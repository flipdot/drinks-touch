import io

import pygame

from config import Color
from .base import BaseIcon


def load_and_scale_svg(filename, scale):
    svg_string = open(filename, "rt").read()
    start = svg_string.find("<svg")
    if start > 0:
        svg_string = (
            svg_string[: start + 4]
            + f' transform="scale({scale})"'
            + svg_string[start + 4 :]
        )
    return pygame.image.load(io.BytesIO(svg_string.encode()))


class SvgIcon(BaseIcon):

    def __init__(
        self,
        path,
        pos=None,
        color: Color | None = None,
        width=None,
        height=None,
        *args,
        **kwargs,
    ):
        """
        If one of width or height is set and the other is None, the other
        will be calculated to keep the aspect ratio.
        """
        super().__init__(pos=pos, *args, **kwargs)
        self.path = path
        image = pygame.image.load(self.path).convert_alpha()
        # image = load_and_scale_svg(self.path, 2)
        if color:
            image.fill(color.value, special_flags=pygame.BLEND_RGBA_MIN)

        if width and height is None:
            aspect_ratio = image.get_width() / image.get_height()
            height = int(width / aspect_ratio)
        elif height and width is None:
            aspect_ratio = image.get_height() / image.get_width()
            width = int(height / aspect_ratio)

        if width and height:
            self.image = pygame.transform.smoothscale(image, (width, height))
            self.width = width
            self.height = height
        else:
            self.image = image
            self.width = image.get_width()
            self.height = image.get_height()

    def draw(self, surface):
        surface.blit(self.image, (0, 0))
