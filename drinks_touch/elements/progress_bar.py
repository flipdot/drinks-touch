import math

import pygame.draw

from config import COLORS, FONTS
from elements.base_elm import BaseElm


class ProgressBar(BaseElm):

    def __init__(
        self,
        pos=None,
        bar_height=30,
        box_height=150,
        width=100,
        label=None,
        text=None,
        padding: (
            int | tuple[int, int] | tuple[int, int, int] | tuple[int, int, int, int]
        ) = 5,
        *args,
        **kwargs
    ):
        super(ProgressBar, self).__init__(
            pos=pos,
            width=width,
            padding=padding,
            *args,
            **kwargs,
        )
        self.bar_height = bar_height
        self.text_height = box_height
        self.label = label
        self.label_height = 0
        self.text = text
        self.max_line_length = math.floor(
            (width - self.padding_left - self.padding_right) / 9
        )
        self.max_lines = math.floor(box_height / 15)

        self.color = COLORS["infragelb"]
        self.percent = None
        self.tick = 0

    @property
    def pos_label(self):
        return self.pos

    @property
    def pos_bar(self):
        if self.label:
            return self.pos_label[0], self.pos_label[1] + self.label_height
        return self.pos_label

    @property
    def pos_textbox(self):
        return self.pos_bar[0], self.pos_bar[1] + self.bar_height

    @property
    def height(self):
        h = self.bar_height
        if self.label:
            # TODO: calculate label height instead of rendering it
            surface = self._render_label()
            h += surface.get_height()
        if self.text:
            # TODO: calculate text height instead of rendering it
            surface = self._render_textbox()
            h += surface.get_height()
        return h

    @property
    def width(self):
        return self._width

    def success(self):
        self.color = (0, 255, 0)
        if self.percent is None:
            self.percent = 1

    def fail(self):
        self.color = (255, 0, 0)
        if self.percent is None:
            self.percent = 1

    def reset(self):
        self.color = COLORS["infragelb"]
        self.percent = None

    def render(self, dt, *args, **kwargs) -> pygame.Surface:
        self.tick += dt
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        x = 0
        y = 0

        if self.label:
            label = self._render_label()
            surface.blit(label, (x, y))
            y += label.get_height()
        bar = self._render_bar()
        surface.blit(bar, (x, y))
        y += bar.get_height()
        if self.text:
            text = self._render_textbox()
            surface.blit(text, (x, y))
            y += text.get_height()
        return surface

    def _render_label(self) -> pygame.Surface:
        font = pygame.font.SysFont("sans serif", 25)
        label = font.render(self.label, 1, self.color)
        return label

    def _render_textbox(self) -> pygame.Surface:
        surface = pygame.Surface((self.width, self.text_height), pygame.SRCALPHA)
        pygame.draw.rect(
            surface,
            self.color,
            (
                0,
                0,
                self.width,
                self.text_height,
            ),
            width=1,
        )
        font = pygame.font.SysFont(FONTS["monospace"], 15)

        lines = self.text.split("\n")

        # split lines that are too long
        for i, line in enumerate(lines):
            if len(line) > self.max_line_length:
                lines.pop(i)
                while len(line) > self.max_line_length:
                    lines.insert(i, line[: self.max_line_length])
                    line = line[self.max_line_length :].strip()
                lines.insert(i + 1, line)

        last_lines = lines[-self.max_lines :]

        for i, line in enumerate(last_lines):
            text = font.render(line, 1, (246, 198, 0))
            surface.blit(
                text,
                (
                    self.padding_left,
                    self.padding_top + i * 15,
                ),
            )
        return surface

    def _render_bar(self) -> pygame.Surface:
        surface = pygame.Surface((self.width, self.bar_height), pygame.SRCALPHA)
        pygame.draw.rect(
            surface,
            self.color,
            (0, 0, self.width, self.bar_height),
            width=2,
        )
        if self.percent is not None:
            pygame.draw.rect(
                surface,
                self.color,
                (
                    0,
                    0,
                    self.width * self.percent,
                    self.bar_height,
                ),
            )
        else:
            inner_width = self.width * 0.3
            cx, y = 0, 0
            cx -= inner_width / 2

            cx += self.tick * 300 % (self.width + inner_width)

            x = cx - inner_width / 2
            width = inner_width

            pygame.draw.rect(
                surface,
                self.color,
                (x, y, width, self.bar_height),
            )
        return surface
