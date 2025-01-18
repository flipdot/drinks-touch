from .base_elm import BaseElm

import contextlib

with contextlib.redirect_stdout(None):
    import pygame


class Image(BaseElm):
    def __init__(self, src, size=None, scale_smooth=True, *args, **kwargs):
        self.src = src
        self.size = size
        self.img = pygame.image.load(self.src).convert_alpha()

        if size:
            if scale_smooth:
                self.img = pygame.transform.smoothscale(self.img, size)
            else:
                self.img = pygame.transform.scale(self.img, size)

        super().__init__(
            *args, height=self.img.get_height(), width=self.img.get_width(), **kwargs
        )

    def render(self, *args, **kwargs) -> pygame.Surface:
        return self.img
