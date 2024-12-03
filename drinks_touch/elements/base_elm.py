import pygame
from pygame import Surface


class BaseElm:
    def __init__(
        self,
        children: list["BaseElm"] | None = None,
        pos=None,
        height=None,
        width=None,
        align_right=False,
        align_bottom=False,
        padding: (
            int | tuple[int, int] | tuple[int, int, int] | tuple[int, int, int, int]
        ) = 0,
    ):
        if pos is None:
            pos = (0, 0)
        self.pos = pos
        self._height = height
        self._width = width
        self.is_visible = True
        self.align_right = align_right
        self.align_bottom = align_bottom
        self.focus = False
        if children is None:
            children = []
        self.children = children
        if not isinstance(padding, tuple):
            self.padding_top = padding
            self.padding_right = padding
            self.padding_bottom = padding
            self.padding_left = padding
        elif len(padding) == 2:
            self.padding_top = padding[0]
            self.padding_right = padding[1]
            self.padding_bottom = padding[0]
            self.padding_left = padding[1]
        elif len(padding) == 3:
            self.padding_top = padding[0]
            self.padding_right = padding[1]
            self.padding_bottom = padding[2]
            self.padding_left = padding[1]
        else:
            self.padding_top = padding[0]
            self.padding_right = padding[1]
            self.padding_bottom = padding[2]
            self.padding_left = padding[3]

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

    def event(self, event, pos=None):
        if pos is None and hasattr(event, "pos"):
            pos = event.pos
        if pos is None:
            return
        collides = self.collides_with(pos)
        transformed_pos = (
            pos[0] - self.screen_pos[0],
            pos[1] - self.screen_pos[1],
        )

        for child in self.children:
            if hasattr(event, "consumed") and event.consumed:
                return
            child.event(event, transformed_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if collides:
                self.focus = True
                event.consumed = True
            else:
                self.focus = False

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:

            if self.focus and collides:
                if hasattr(self, "on_click"):
                    self.on_click(*transformed_pos)
                event.consumed = True
            self.focus = False

    @property
    def visible(self):
        # TODO get rid of is_visible
        return self.is_visible

    def collides_with(self, pos: tuple[int, int]) -> bool:
        return (
            self.box is not None
            and self.visible
            and pygame.Rect(self.box).collidepoint(pos[0], pos[1])
        )

    def render(self, *args, **kwargs) -> Surface:
        surface = pygame.font.SysFont("monospace", 25).render(
            "Return surface in render()", 1, (255, 0, 255)
        )
        return surface

    def render_debug(self) -> pygame.Surface:
        w = self.width
        h = self.height
        surface = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surface, (255, 0, 255), (0, 0, w, h), 1)
        pygame.draw.line(surface, (255, 0, 255), (0, 0), (w, h))
        pygame.draw.line(surface, (255, 0, 255), (0, h), (w, 0))
        return surface
