from __future__ import annotations

import enum
import logging

import pygame

from config import Color, Font
from elements.base_elm import BaseElm
from overlays.keyboard import KeyboardLayout
from screens.screen_manager import ScreenManager


logger = logging.getLogger(__name__)


class InputType(enum.Enum):
    TEXT = "text"
    NUMBER = "number"
    POSITIVE_NUMBER = "positive_number"


NUMERIC = "0123456789"
ALPHABET = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "àáâãäåæçèéêëìíîïðñòóôõöøùúûüýÿ"
    "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝ"
    "ßẞ"
)
ALPHA_NUMERIC = NUMERIC + ALPHABET


class InputField(BaseElm):

    def __init__(
        self,
        *args,
        width,
        height,
        input_type=InputType.TEXT,
        auto_complete: callable | None = None,
        only_auto_complete: bool = False,
        **kwargs,
    ):
        """
        auto_complete can be a function that takes the current text and returns a list of suggestions.
        If only_auto_complete is True, the user can only select from the suggestions.
        """
        assert (
            not only_auto_complete or auto_complete
        ), "only_auto_complete requires auto_complete function"
        if input_type in [InputType.NUMBER, InputType.POSITIVE_NUMBER]:
            self.valid_chars = NUMERIC + ".,"
            if input_type == InputType.NUMBER:
                self.valid_chars += "-"
            self.max_decimal_places = kwargs.pop("max_decimal_places", None)
        elif input_type == InputType.TEXT:
            self.valid_chars = ALPHA_NUMERIC + " ,.-_"

        super().__init__(*args, **kwargs, width=width, height=height)
        self.input_type = input_type
        self.auto_complete = auto_complete
        self.only_auto_complete = only_auto_complete
        self.text = ""

    @property
    def keyboard_settings(self):
        if self.input_type == InputType.NUMBER:
            layout = KeyboardLayout.NUMERIC
        else:
            layout = KeyboardLayout.DEFAULT
        return {"enabled": True, "layout": layout}

    def render(self, *args, **kwargs):
        is_active = ScreenManager.get_instance().active_object is self
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(
            surface, Color.NAVBAR_BACKGROUND.value, (0, 0, self.width, self.height)
        )
        pygame.draw.rect(surface, Color.BLACK.value, (0, 0, self.width, self.height), 1)
        pygame.draw.line(
            surface,
            Color.PRIMARY.value,
            (0, self.height - 1),
            (self.width, self.height - 1),
        )
        font = pygame.font.Font(Font.SANS_SERIF.value, self.height - 10)
        text_surface = font.render(self.text, 1, Color.PRIMARY.value)
        surface.blit(text_surface, (5, 0))
        if is_active:
            pygame.draw.rect(
                surface, Color.PRIMARY.value, (0, 0, self.width, self.height), 1
            )

            # blinking cursor
            if self.ts // 1 % 2 == 0:
                x = text_surface.get_width() + 5
                pygame.draw.line(
                    surface, Color.PRIMARY.value, (x, 5), (x, self.height - 5), 2
                )
        return surface

    def render_overlay(self, *args, **kwargs):
        if not self.auto_complete:
            return
        is_active = ScreenManager.get_instance().active_object is self
        if not is_active:
            return

        suggestions = self.auto_complete(self.text)
        surface = pygame.Surface(
            (self.width, self.height + len(suggestions) * self.height), pygame.SRCALPHA
        )
        font = pygame.font.Font(Font.SANS_SERIF.value, self.height - 10)

        if suggestions:
            if len(suggestions) == 1 and suggestions[0] == self.text:
                return
            suggestion_surface = pygame.Surface(
                (self.width, len(suggestions) * self.height)
            )
            for i, suggestion in enumerate(suggestions):
                suggestion_text = font.render(suggestion, 1, Color.PRIMARY.value)
                suggestion_surface.blit(suggestion_text, (5, i * self.height))
            surface.blit(suggestion_surface, (0, self.height))
        return surface

    def key_event(self, event: pygame.event.Event):
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
            return

        char = event.unicode
        if not char:
            # not a printable character
            return
        if char not in self.valid_chars:
            return
        char = event.unicode
        if self.input_type in (InputType.NUMBER, InputType.POSITIVE_NUMBER):
            if char == "-" and self.text:
                # only allow minus at the start
                return
            if char in ",.":
                # only allow one decimal point, and convert comma to period
                if "." in self.text:
                    return
                char = "."
            if "." in self.text and self.max_decimal_places is not None:
                before_comma, _, after_comma = self.text.partition(".")
                if len(after_comma) >= self.max_decimal_places:
                    return

        if self.only_auto_complete:
            suggestions = self.auto_complete(self.text + char)
            if not suggestions:
                return
            if len(suggestions) == 1:
                self.text = suggestions[0]
                return
        self.text += char
