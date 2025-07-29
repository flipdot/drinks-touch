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
        width=None,
        height=None,
        size=30,
        text=None,
        color=Color.PRIMARY,
        bg_color=Color.BUTTON_BACKGROUND,
        disabled_color=Color.DISABLED,
        on_click=None,
        inner: BaseElm | None = None,
        pos=(0, 0),
        padding: (
            int | tuple[int, int] | tuple[int, int, int] | tuple[int, int, int, int]
        ) = 10,
        disabled=False,
        pass_on_click_kwargs=False,
        min_width=None,
        min_height=None,
        max_width=None,
        max_height=None,
        *args,
        **kwargs,
    ):
        from . import Label

        super().__init__(children, pos, None, None, *args, padding=padding, **kwargs)

        self.bg_color = bg_color
        self.color = color
        self._color = color
        self._disabled_color = disabled_color
        self.on_click_handler = on_click
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height
        if inner is None:
            inner = Label(
                pos=(self.pos[0] + self.padding_left, self.pos[1] + self.padding_top),
                text=text,
                font=font,
                size=size,
                color=color,
            )
        self.inner = inner
        if width is not None:
            if max_width is not None:
                raise ValueError("Cannot set both width and max_width")
            if min_width is not None:
                raise ValueError("Cannot set both width and min_width")
            self.max_width = self.min_width = width
        if height is not None:
            if max_height is not None:
                raise ValueError("Cannot set both height and max_height")
            if min_height is not None:
                raise ValueError("Cannot set both height and min_height")
            self.max_height = self.min_height = height
        self.width = self.inner.width + self.padding_left + self.padding_right
        self.height = self.inner.height + self.padding_top + self.padding_bottom
        self.disabled = disabled
        self.pass_on_click_kwargs = pass_on_click_kwargs

    def calculate_hash(self):
        super_hash = super().calculate_hash()
        properties = (
            self.disabled,
            self.bg_color,
            self.focus,
        )
        if self.inner:
            return hash((super_hash, properties, self.inner.calculate_hash()))
        return hash((super_hash, properties))

    @property
    def text(self):
        return self.inner.text

    @text.setter
    def text(self, value):
        self.inner.text = value

    @property
    def disabled(self) -> bool:
        return self._disabled

    @disabled.setter
    def disabled(self, value: bool):
        self._disabled = value
        if value:
            self.color = self._disabled_color
        else:
            self.color = self._color
        self.inner.color = self.color

    @BaseElm.height.setter
    def height(self, value):
        if self.min_height is not None:
            value = max(value, self.min_height)
        if self.max_height is not None:
            value = min(value, self.max_height)
        self._height = value

    @BaseElm.width.setter
    def width(self, value):
        if self.min_width is not None:
            value = max(value, self.min_width)
        if self.max_width is not None:
            value = min(value, self.max_width)
        self._width = value

    def __repr__(self):
        if hasattr(self.inner, "text"):
            text = self.inner.text
        else:
            text = str(self.inner)
        return f"<Button {text}>"

    def _render(self, *args, **kwargs) -> pygame.Surface:
        inner = self.inner._render(*args, **kwargs)

        self.width = self.inner.width + self.padding_left + self.padding_right
        self.height = self.inner.height + self.padding_top + self.padding_bottom

        size = (self.width, self.height)

        surface = pygame.Surface(size, pygame.SRCALPHA)
        if self.focus:
            surface.fill(tuple(c * 0.7 for c in self.color.value), (0, 0, *size))
        else:
            surface.fill(self.bg_color.value, (0, 0, *size))

        if inner is not None:
            surface.blit(inner, (self.padding_left, self.padding_top))
        pygame.draw.rect(surface, self.color.value, (0, 0, *size), 1)
        return surface

    def on_click(self, x, y):
        if self.disabled:
            return
        if self.on_click_handler is None:
            raise NotImplementedError("No on_click handler defined")
        if self.pass_on_click_kwargs:
            self.on_click_handler(button=self)
        else:
            self.on_click_handler()
