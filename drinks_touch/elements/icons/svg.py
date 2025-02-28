import functools
import io
from datetime import datetime
from random import random

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
        image = SvgIcon.load_image(path, color)

        img_width = image.get_width()
        img_height = image.get_height()
        if width and height is None:
            aspect_ratio = img_width / img_height
            height = int(width / aspect_ratio)
        elif height and width is None:
            aspect_ratio = img_height / img_width
            width = int(height / aspect_ratio)

        if width and height:
            self.image = pygame.transform.smoothscale(image, (width, height))
            self.width = width + self.padding_left + self.padding_right
            self.height = height + self.padding_top + self.padding_bottom
        else:
            self.image = image
            self.width = img_width + self.padding_left + self.padding_right
            self.height = img_height + self.padding_top + self.padding_bottom

        today = datetime.now().date()
        april_fools = today.month == 4 and today.day == 1
        if april_fools:
            self.image = pygame.transform.flip(
                self.image, random() > 0.5, random() > 0.5
            )

    @classmethod
    @functools.cache
    def load_image(cls, path, color: Color | None = None):
        image = pygame.image.load(path).convert_alpha()
        if color:
            image.fill(color.value, special_flags=pygame.BLEND_RGBA_MIN)
        return image

    def draw(self, surface):
        surface.blit(self.image, (self.padding_left, self.padding_top))
