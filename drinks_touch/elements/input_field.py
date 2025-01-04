from __future__ import annotations

import enum
import logging

import pygame

from config import Color, Font
from elements.base_elm import BaseElm
from screens.screen_manager import ScreenManager


logger = logging.getLogger(__name__)


class InputType(enum.Enum):
    TEXT = "text"
    NUMBER = "number"
    POSITIVE_NUMBER = "positive_number"


NUMERIC = list(range(pygame.K_0, pygame.K_9 + 1))
ALPHABET = list(range(pygame.K_a, pygame.K_z + 1)) + [
    223,  # ß
    228,  # ä
    246,  # ö
    252,  # ü
]
ALPHA_NUMERIC = NUMERIC + ALPHABET


class InputField(BaseElm):

    def __init__(self, *args, width, height, input_type=InputType.TEXT, **kwargs):
        if input_type in [InputType.NUMBER, InputType.POSITIVE_NUMBER]:
            self.valid_chars = NUMERIC + [
                pygame.K_PERIOD,
                pygame.K_COMMA,
            ]
            if input_type == InputType.NUMBER:
                self.valid_chars.append(pygame.K_MINUS)
            self.max_decimal_places = kwargs.pop("max_decimal_places", None)
        elif input_type == InputType.TEXT:
            self.valid_chars = ALPHA_NUMERIC + [
                pygame.K_SPACE,
                pygame.K_COMMA,
                pygame.K_PERIOD,
                pygame.K_MINUS,
                pygame.K_UNDERSCORE,
            ]

        super().__init__(*args, **kwargs, width=width, height=height)
        self.input_type = input_type
        self.text = ""

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
            if self.ts // 1 % 2 == 0:
                x = text_surface.get_width() + 5
                pygame.draw.line(
                    surface, Color.PRIMARY.value, (x, 5), (x, self.height - 5), 2
                )
        return surface

    def key_event(self, event: pygame.event.Event):
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.key in self.valid_chars:
            char = event.unicode
            if self.input_type in (InputType.NUMBER, InputType.POSITIVE_NUMBER):
                if event.key == pygame.K_MINUS and self.text:
                    # only allow minus at the start
                    return
                if event.key in (pygame.K_PERIOD, pygame.K_COMMA):
                    # only allow one decimal point, and convert comma to period
                    if "." in self.text:
                        return
                    char = "."
                if "." in self.text and self.max_decimal_places is not None:
                    before_comma, _, after_comma = self.text.partition(".")
                    if len(after_comma) >= self.max_decimal_places:
                        return
            self.text += char
        else:
            logger.info(f"Invalid key: {event.key}")
