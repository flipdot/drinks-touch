import functools
import io
from datetime import datetime
from pathlib import Path
from random import random

import pygame
import cairosvg

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
        self.path = Path(path)
        self.color = color
        image = SvgIcon.load_image(path, color, width, height)

        img_width = image.get_width()
        img_height = image.get_height()

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
    def load_image(
        cls, path: str | Path, color: Color | None = None, width=None, height=None
    ):
        png_bytes = cairosvg.svg2png(
            url=str(path), output_width=width, output_height=height
        )
        image = pygame.image.load(io.BytesIO(png_bytes)).convert_alpha()
        if color:
            image.fill(color.value, special_flags=pygame.BLEND_RGBA_MIN)
        return image

    def draw(self, surface):
        surface.blit(self.image, (self.padding_left, self.padding_top))
