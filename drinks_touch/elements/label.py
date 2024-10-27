import config
from .base_elm import BaseElm

import contextlib

with contextlib.redirect_stdout(None):
    import pygame

pygame.font.init()


class Label(BaseElm):
    _font_cache = {}

    def __init__(
        self,
        children: list["BaseElm"] | None = None,
        text="<Label>",
        font=config.FONTS["sans serif"],
        size=35,
        color=config.COLORS["infragelb"],
        bg_color=None,
        border_color=None,
        border_width=0,
        blink_frequency=0,
        max_width=None,
        *args,
        **kwargs,
    ):
        self.size = size
        self.max_width = max_width
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width
        self.blink_frequency = blink_frequency

        self.frame_counter = 0
        super().__init__(children, height=self.size, width=self.size, *args, **kwargs)

        self.font = Label.get_font(font, self.size)

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
