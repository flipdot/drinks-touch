from config import COLORS
from .base_elm import BaseElm

import contextlib

with contextlib.redirect_stdout(None):
    import pygame

pygame.font.init()


class Label(BaseElm):
    _font_cache = {}

    def __init__(self, *args, **kwargs):
        self.font_face = kwargs.get("font", "sans serif")
        self.size = kwargs.get("size", 50)
        self.max_width = kwargs.get("max_width", None)
        # if True, pos marks top-right instead of top-left corner
        self.align_right = kwargs.get("align_right", False)
        self.text = kwargs.get("text", "<Label>")
        self.color = kwargs.get("color", COLORS["infragelb"])
        self.bg_color = kwargs.get("bg_color", None)
        self.border_color = kwargs.get("border_color", None)
        self.border_width = kwargs.get("border_width", 0)
        self.padding = kwargs.get("padding", 0)
        self.blink_frequency = kwargs.get("blink_frequency", 0)

        self.frame_counter = 0
        pos = kwargs.pop("pos", (0, 0))
        super().__init__(pos, self.size, self.size, *args, **kwargs)

        self.font = Label.get_font(self.font_face, self.size)

    @classmethod
    def get_font(cls, font_face, size):
        if (font_face, size) not in cls._font_cache:
            font = pygame.font.SysFont(font_face, size)
            cls._font_cache[(font_face, size)] = font
        return cls._font_cache[(font_face, size)]

    def render(self, *args, **kwargs) -> pygame.Surface | None:
        self.frame_counter += 1
        if self.blink_frequency:
            if (self.frame_counter // self.blink_frequency) % 2:
                return

        text, pos, area = self._build_text()
        self.width = area.width
        self.height = area.height
        bg = self._render_background(area)
        surface = pygame.Surface((area.width, area.height), pygame.SRCALPHA)
        if bg:
            surface.blit(bg, (0, 0), area)
        surface.blit(text, (0, 0), area)
        return surface

    def _render_background(self, area: pygame.Rect) -> pygame.Surface | None:
        if not self.bg_color:
            return
        size = (
            area.width + 2 * self.padding,
            area.height + 2 * self.padding,
        )
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(self.bg_color)
        return surface

    def _build_text(self):
        elm = self.font.render(self.text, 1, self.color)
        cutx = 0
        pos = self.pos
        if self.align_right:
            if self.max_width:
                align_width = min(self.max_width, elm.get_width())
                cutx = max(0, elm.get_width() - self.max_width)
            else:
                align_width = elm.get_width()
            pos = (self.pos[0] - align_width, self.pos[1])

        area = pygame.Rect(
            cutx,
            0,
            self.max_width if self.max_width else elm.get_width(),
            elm.get_height(),
        )

        return elm, pos, area
