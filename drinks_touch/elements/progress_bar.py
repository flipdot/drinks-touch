import math

import pygame.draw

from elements.base_elm import BaseElm


class ProgressBar(BaseElm):

    def __init__(
        self,
        screen,
        pos,
        bar_height=30,
        text_height=150,
        width=460,
        label=None,
        text=None,
    ):
        super(ProgressBar, self).__init__(screen, pos, bar_height + text_height, width)
        self.bar_height = bar_height
        self.text_height = text_height
        self.label = label
        self.text = text
        self.padding = 5
        self.max_line_length = math.floor(width / 9.2)
        self.max_lines = math.floor(text_height / 15)

        self.color = (246, 198, 0)
        self.percent = None
        self.tick = 0

    def success(self):
        self.color = (0, 255, 0)
        self.percent = 1

    def fail(self):
        self.color = (255, 0, 0)
        self.percent = 1

    def render(self, dt, *args, **kwargs):
        self.tick += dt
        self._render_bar()
        if self.label:
            self._render_label()
        if self.text:
            self._render_textbox()

    def _render_label(self):
        font = pygame.font.SysFont("sans serif", 25)
        label = font.render(self.label, 1, self.color)
        self.screen.blit(label, (self.pos[0], self.pos[1] - 25))

    def _render_textbox(self):
        pygame.draw.rect(
            self.screen,
            self.color,
            (
                self.pos[0],
                self.pos[1] + self.bar_height,
                self.width,
                self.text_height,
            ),
            width=1,
        )
        font = pygame.font.SysFont("monospace", 15)

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
                    self.pos[0] + self.padding,
                    self.pos[1] + self.bar_height + self.padding + i * 15,
                ),
            )

    def _render_bar(self):
        pygame.draw.rect(
            self.screen,
            self.color,
            (self.pos[0], self.pos[1], self.width, self.bar_height),
            width=2,
        )
        if self.percent is not None:
            pygame.draw.rect(
                self.screen,
                self.color,
                (self.pos[0], self.pos[1], self.width * self.percent, self.bar_height),
            )
        else:
            inner_width = self.width * 0.3
            cx, y = self.pos
            cx -= inner_width / 2

            cx += self.tick * 300 % (self.width + inner_width)

            x = cx - inner_width / 2
            width = inner_width
            if x < self.pos[0]:
                width -= self.pos[0] - x
                x = self.pos[0]
            if width + x > self.pos[0] + self.width:
                width = self.pos[0] + self.width - x

            pygame.draw.rect(
                self.screen,
                self.color,
                (x, y, width, self.bar_height),
            )
