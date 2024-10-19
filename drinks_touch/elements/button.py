from config import FONTS, COLORS
from .base_elm import BaseElm

import contextlib

with contextlib.redirect_stdout(None):
    import pygame


class Button(BaseElm):
    def __init__(
        self,
        screen,
        font=FONTS["monospace"],
        size=30,
        text="<Label>",
        color=COLORS["infragelb"],
        click_func=None,
        click_func_param=None,
        click_param=None,
        padding: (
            int | tuple[int, int] | tuple[int, int, int] | tuple[int, int, int, int]
        ) = 10,
        force_width=None,
        force_height=None,
        inner: BaseElm = None,
        pos=(0, 0),
    ):
        from . import Label

        super(Button, self).__init__(screen, pos, size, -1)

        self.size = size
        self.color = color
        self.clicked = click_func or self.__clicked
        self.clicked_param = click_func_param
        self.click_param = click_param

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
        self.force_width = force_width
        self.force_height = force_height
        if inner is None:
            inner = Label(
                screen,
                pos=(self.pos[0] + self.padding_left, self.pos[1] + self.padding_top),
                text=text,
                font=font,
                size=size,
                color=color,
            )
        self.inner = inner

        self.box = None
        self.clicking = False

    @staticmethod
    def __clicked():
        print("Clicked on button without handler")

    def pre_click(self):
        self.clicking = True

    def post_click(self):
        self.clicking = False

    def render(self, *args, **kwargs):
        if self.clicking:
            self.screen.fill(tuple(c * 0.7 for c in self.color), self.box)

        self.inner.render(*args, **kwargs)

        self.box = (
            self.inner.pos[0] - self.padding_left,
            self.inner.pos[1] - self.padding_top,
            self.inner.width + self.padding_left + self.padding_right,
            self.inner.height + self.padding_top + self.padding_bottom,
        )

        pygame.draw.rect(self.screen, self.color, self.box, 1)

    def events(self, events):
        for event in events:
            if "consumed" in event.dict and event.consumed:
                continue

            if event.type == pygame.MOUSEBUTTONUP:
                pos = event.pos

                if (
                    self.box is not None
                    and self.visible()
                    and pygame.Rect(self.box).collidepoint(pos[0], pos[1])
                ):
                    self.pre_click()
                    try:
                        if self.click_param:
                            self.clicked_param(self.click_param)
                        else:
                            self.clicked()
                    finally:
                        self.post_click()
                    event.consumed = True
