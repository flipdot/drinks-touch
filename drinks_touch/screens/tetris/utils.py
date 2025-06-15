import functools

import pygame
from pygame import Vector3

from config import Color
from screens.tetris.constants import SCALE, SPRITE_RESOLUTION


@functools.lru_cache(maxsize=16)
def get_sprite(sprite_name: str) -> pygame.Surface:
    return pygame.transform.scale(
        pygame.image.load(
            f"drinks_touch/resources/images/tetris/{sprite_name}.png"
        ).convert_alpha(),
        SPRITE_RESOLUTION * SCALE,
    )


def darken(color: Color | tuple[int, int, int], factor: float) -> Vector3:
    if isinstance(color, Color):
        v = color.value[:3]
    else:
        v = color[:3]
    return Vector3(*v) * (1 - factor)


def lighten(color: Color | tuple[int, int, int], factor: float) -> Vector3:
    if isinstance(color, Color):
        v = color.value[:3]
    else:
        v = color[:3]
    return Vector3(*v) * (1 - factor) + Vector3(255, 255, 255) * factor


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min(value, max_value), min_value)
