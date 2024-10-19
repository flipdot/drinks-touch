import math

import pygame.draw

from config import FONTS
from elements.base_elm import BaseElm


class ProgressBar(BaseElm):

    def __init__(
        self,
        screen,
        pos=None,
        bar_height=30,
        box_height=150,
        width=460,
        label=None,
        text=None,
    ):
        super(ProgressBar, self).__init__(
            screen,
            pos=pos,
            width=width,
        )
        self.bar_height = bar_height
        self.text_height = box_height
        self.label = label
        self.label_height = None
        self.text = text
        self.padding = 5
        self.max_line_length = math.floor(width / 9.2)
        self.max_lines = math.floor(box_height / 15)

        self.color = (246, 198, 0)
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
            h += self.label_height
        if self.text:
            h += self.text_height
        return h

    def success(self):
        self.color = (0, 255, 0)
        if self.percent is None:
            self.percent = 1

    def fail(self):
        self.color = (255, 0, 0)
        if self.percent is None:
            self.percent = 1

    def render(self, dt, *args, **kwargs):
        self.tick += dt
        if self.label:
            self._render_label()
        self._render_bar()
        if self.text:
            self._render_textbox()

    def _render_label(self):
        font = pygame.font.SysFont(FONTS["sans serif"], 22)
        label = font.render(self.label, 1, self.color)
        self.label_height = label.get_height()
        self.screen.blit(label, self.pos_label)

    def _render_textbox(self):
        pygame.draw.rect(
            self.screen,
            self.color,
            (
                self.pos_textbox[0],
                self.pos_textbox[1],
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
            self.screen.blit(
                text,
                (
                    self.pos_textbox[0] + self.padding,
                    self.pos_textbox[1] + self.padding + i * 15,
                ),
            )

    def _render_bar(self):
        pygame.draw.rect(
            self.screen,
            self.color,
            (self.pos_bar[0], self.pos_bar[1], self.width, self.bar_height),
            width=2,
        )
        if self.percent is not None:
            pygame.draw.rect(
                self.screen,
                self.color,
                (
                    self.pos_bar[0],
                    self.pos_bar[1],
                    self.width * self.percent,
                    self.bar_height,
                ),
            )
        else:
            inner_width = self.width * 0.3
            cx, y = self.pos_bar
            cx -= inner_width / 2

            cx += self.tick * 300 % (self.width + inner_width)

            x = cx - inner_width / 2
            width = inner_width
            if x < self.pos_bar[0]:
                width -= self.pos_bar[0] - x
                x = self.pos_bar[0]
            if width + x > self.pos_bar[0] + self.width:
                width = self.pos_bar[0] + self.width - x

            pygame.draw.rect(
                self.screen,
                self.color,
                (x, y, width, self.bar_height),
            )
