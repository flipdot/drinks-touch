import math

import pygame.draw

import config
from config import Color
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

        self.color = Color.PRIMARY
        self.percent = None
        self.forever_bar_pos = 0
        self.font = pygame.font.SysFont("sans serif", 25)
        self.font_mono = pygame.font.Font(config.Font.MONOSPACE.value, 15)

    def calculate_hash(self):
        super_hash = super().calculate_hash()
        return hash(
            (
                super_hash,
                self.bar_height,
                self.text_height,
                self.label,
                self.text,
                self.label_height,
                self.color,
                self.percent,
                self.forever_bar_pos,
            )
        )

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
            h += self.font.size(self.label)[1]
        if self.text:
            h += self.text_height
        return h

    @property
    def width(self):
        return self._width

    def success(self):
        self.color = Color.SUCCESS
        if self.percent is None:
            self.percent = 1

    def fail(self):
        self.color = Color.ERROR
        if self.percent is None:
            self.percent = 1

    def reset(self):
        self.color = Color.PRIMARY
        self.percent = None

    def tick(self, dt: float):
        if not self.percent:
            self.forever_bar_pos += dt * 300

    def _render(self, *args, **kwargs) -> pygame.Surface:
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        x = 0
        y = 0

        if self.label:
            label = self._render_label()
            surface.blit(label, (x, y))
            y += label.get_height()
        bar = self._render_bar()
        surface.blit(bar, (x, y))
        y += self.bar_height
        if self.text:
            text = self._render_textbox()
            surface.blit(text, (x, y))
            y += text.get_height()
        return surface

    def _render_label(self) -> pygame.Surface:
        label = self.font.render(self.label, 1, self.color.value)
        return label

    def _render_textbox(self) -> pygame.Surface:
        surface = pygame.Surface((self.width, self.text_height), pygame.SRCALPHA)
        pygame.draw.rect(
            surface,
            self.color.value,
            (
                0,
                0,
                self.width,
                self.text_height,
            ),
            width=1,
        )

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
            text = self.font_mono.render(line, 1, config.Color.PRIMARY.value)
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
            self.color.value,
            (0, 0, self.width, self.bar_height),
            width=2,
        )
        if self.percent is not None:
            pygame.draw.rect(
                surface,
                self.color.value,
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

            # cx += self.tick * 300 % (self.width + inner_width)
            cx += self.forever_bar_pos % (self.width + inner_width)

            x = cx - inner_width / 2
            width = inner_width

            pygame.draw.rect(
                surface,
                self.color.value,
                (x, y, width, self.bar_height),
            )
        return surface
