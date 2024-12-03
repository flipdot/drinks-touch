from .base_elm import BaseElm

import contextlib

with contextlib.redirect_stdout(None):
    import pygame


class Image(BaseElm):
    def __init__(self, src, size=None, *args, **kwargs):
        self.src = src
        self.size = size
        self.img = pygame.image.load(self.src).convert_alpha()

        if size:
            self.img = pygame.transform.smoothscale(self.img, size)
        super(Image, self).__init__(*args, **kwargs)

    @property
    def width(self):
        return self.img.get_width()

    @property
    def height(self):
        return self.img.get_height()

    def render(self, *args, **kwargs) -> pygame.Surface:
        return self.img
