from .base_elm import BaseElm

import contextlib

with contextlib.redirect_stdout(None):
    import pygame


class Image(BaseElm):
    def __init__(self, **kwargs):
        self.pos = kwargs.get("pos", (0, 0))
        self.src = kwargs.get("src", "drinks_touch/resources/images/test.jpg")
        self.size = kwargs.get("size", None)
        self.img = pygame.image.load(self.src).convert_alpha()

        pos = kwargs.get("pos", (0, 0))
        if self.size:
            self.img = pygame.transform.smoothscale(self.img, self.size)
        img_size = self.img.get_size()
        super(Image, self).__init__(None, pos, img_size[1], img_size[0])

    def render(self, *args, **kwargs) -> pygame.Surface:
        return self.img
