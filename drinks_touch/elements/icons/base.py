import pygame

from config import Color
from elements.base_elm import BaseElm


class BaseIcon(BaseElm):
    SIZE = 24
    COLOR = Color.PRIMARY

    def __init__(
        self,
        pos=None,
        width=None,
        height=None,
        visible=True,
        bg_color: Color | None = None,
        padding: (
            int
            | tuple[int, int]
            | tuple[int, int, int]
            | tuple[int, int, int, int]
            | None
        ) = 0,
    ):
        super().__init__(pos=pos)
        self.visible = visible
        self.bg_color = bg_color
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
        self.width = (width or self.SIZE) + self.padding_left + self.padding_right
        self.height = (height or self.SIZE) + self.padding_top + self.padding_bottom

    def _render(self, *args, **kwargs) -> pygame.Surface | None:
        if not self.visible:
            return None
        assert self.pos is not None
        width = self.width + self.padding_left + self.padding_right
        height = self.height + self.padding_top + self.padding_bottom
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        if self.bg_color:
            surface.fill(self.bg_color.value)
        self.draw(surface)
        return surface

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            (255, 0, 255),
            (self.width / 2, self.height / 2),
            self.width / 2,
        )
