from .base_elm import BaseElm

import contextlib

with contextlib.redirect_stdout(None):
    import pygame


class Image(BaseElm):
    def __init__(self, *args, **kwargs):
        self.src = kwargs.get("src", "drinks_touch/resources/images/test.jpg")
        self.size = kwargs.get("size", None)
        self.img = pygame.image.load(self.src).convert_alpha()

        if self.size:
            self.img = pygame.transform.smoothscale(self.img, self.size)
        super(Image, self).__init__(*args, **kwargs)

    @property
    def width(self):
        return self.img.get_width()

    @property
    def height(self):
        return self.img.get_height()

    def render(self, *args, **kwargs) -> pygame.Surface:
        return self.img
