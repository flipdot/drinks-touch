import pygame
from pygame import Surface


class BaseElm(object):
    def __init__(
        self,
        screen,
        pos=None,
        height=None,
        width=None,
        align_right=False,
        align_bottom=False,
        *args,
        **kwargs
    ):
        self.screen = screen
        if pos is None:
            pos = (0, 0)
        self.pos = pos
        self._height = height
        self._width = width
        self.is_visible = True
        self.align_right = align_right
        self.align_bottom = align_bottom

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def screen_pos(self):
        x, y = self.pos
        if self.align_right:
            x -= self.width
        if self.align_bottom:
            y -= self.height
        return x, y

    @property
    def box(self):
        return self.screen_pos + (self.width, self.height)

    # def on_click(self):
    #     pass

    def events(self, events):
        pass

    @property
    def visible(self):
        # TODO get rid of is_visible
        return self.is_visible

    def render(self, *args, **kwargs) -> Surface:
        surface = pygame.font.SysFont("monospace", 25).render(
            "Return surface in render()", 1, (255, 0, 255)
        )
        return surface
