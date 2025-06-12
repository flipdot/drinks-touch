import functools
import random
from datetime import datetime

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
        font: config.Font = config.Font.SANS_SERIF,
        size=35,
        color: config.Color = config.Color.PRIMARY,
        bg_color: config.Color | None = None,
        border_color=None,
        border_width=0,
        blink_frequency=0,
        max_width=None,
        *args,
        **kwargs,
    ):
        assert isinstance(color, config.Color)
        self.size = size
        self.max_width = max_width
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width
        self.blink_frequency = blink_frequency
        today = datetime.now().date()
        april_fools = today.month == 4 and today.day == 1
        if april_fools:
            self.flip_x = random.random() > 0.8
            self.flip_y = random.random() > 0.8
        else:
            self.flip_x = False
            self.flip_y = False

        self.frame_counter = 0
        super().__init__(children, height=self.size, width=self.size, *args, **kwargs)

        self.font = Label.get_font(font, self.size)

    def __repr__(self):
        return f"<Label {self.text}>"

    def calculate_hash(self):
        super_hash = super().calculate_hash()
        return hash(
            (
                super_hash,
                self.text,
                self.flip_x,
                self.flip_y,
                self.color,
                self.bg_color,
                self.border_color,
                self.border_width,
            )
        )

    @classmethod
    @functools.cache
    def get_font(cls, font: config.Font, size):
        return pygame.font.Font(font.value, size)

    def tick(self, dt: float):
        # TODO: Should be independent from frame rate
        if not self.blink_frequency:
            return
        self.frame_counter += 1
        self.visible = (self.frame_counter // self.blink_frequency) % 2 == 0

    def _render(self, *args, **kwargs) -> pygame.Surface | None:
        text, pos, area = self._build_text()
        self.width = area.width + self.padding_left + self.padding_right
        self.height = area.height + self.padding_top + self.padding_bottom
        bg = self._render_background(area)
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        if bg:
            surface.blit(bg, (0, 0), area)
        surface.blit(text, (self.padding_left, self.padding_top), area)
        if self.flip_x or self.flip_y:
            surface = pygame.transform.flip(surface, self.flip_x, self.flip_y)
        return surface

    def _render_background(self, area: pygame.Rect) -> pygame.Surface | None:
        if not self.bg_color:
            return
        size = (
            area.width + self.padding_left + self.padding_right,
            area.height + self.padding_top + self.padding_bottom,
        )
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(self.bg_color.value)
        return surface

    def _build_text(self):
        elm = self.font.render(self.text, 1, self.color.value)
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
