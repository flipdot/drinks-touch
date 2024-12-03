from config import Color, Font
from .base_elm import BaseElm

import contextlib

with contextlib.redirect_stdout(None):
    import pygame


class Button(BaseElm):
    def __init__(
        self,
        children: list["BaseElm"] | None = None,
        font: Font = Font.MONOSPACE,
        size=30,
        text=None,
        color=Color.PRIMARY,
        on_click=None,
        force_width=None,
        force_height=None,
        inner: BaseElm = None,
        pos=(0, 0),
        padding: (
            int | tuple[int, int] | tuple[int, int, int] | tuple[int, int, int, int]
        ) = 10,
        *args,
        **kwargs,
    ):
        from . import Label

        super().__init__(children, pos, size, size, *args, padding=padding, **kwargs)

        self.size = size
        self.color = color
        self.on_click_handler = on_click
        self.force_width = force_width
        self.force_height = force_height
        if inner is None:
            inner = Label(
                pos=(self.pos[0] + self.padding_left, self.pos[1] + self.padding_top),
                text=text,
                font=font,
                size=size,
                color=color,
            )
        self.inner = inner

    def __repr__(self):
        if hasattr(self.inner, "text"):
            text = self.inner.text
        else:
            text = str(self.inner)
        return f"<Button {text}>"

    def render(self, *args, **kwargs) -> pygame.Surface:
        inner = self.inner.render(*args, **kwargs)

        size = (
            self.inner.width + self.padding_left + self.padding_right,
            self.inner.height + self.padding_top + self.padding_bottom,
        )

        self.width = size[0]
        self.height = size[1]

        surface = pygame.Surface(size, pygame.SRCALPHA)
        if self.focus:
            surface.fill(tuple(c * 0.7 for c in self.color.value), (0, 0, *size))
        else:
            surface.fill(Color.BUTTON_BACKGROUND.value, (0, 0, *size))

        if inner is not None:
            surface.blit(inner, (self.padding_left, self.padding_top))
        pygame.draw.rect(surface, self.color.value, (0, 0, *size), 1)
        return surface

    def on_click(self, x, y):
        if self.on_click_handler is None:
            raise NotImplementedError("No on_click handler defined")
        self.on_click_handler()
