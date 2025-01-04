from __future__ import annotations

import enum

import pygame

from config import Color, Font
from elements.base_elm import BaseElm
from screens.screen_manager import ScreenManager


class InputType(enum.Enum):
    TEXT = "text"
    NUMBER = "number"


class InputField(BaseElm):

    def __init__(self, *args, width, height, input_type=InputType.NUMBER, **kwargs):
        super().__init__(*args, **kwargs, width=width, height=height)
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
        surface.blit(text_surface, (5, 5))
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
        elif event.key == pygame.K_RETURN:
            self.text += "\n"
        else:
            self.text += event.unicode
