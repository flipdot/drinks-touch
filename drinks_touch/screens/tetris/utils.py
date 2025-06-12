import functools

import pygame

from screens.tetris.constants import SCALE, SPRITE_RESOLUTION


@functools.lru_cache(maxsize=16)
def get_sprite(sprite_name: str) -> pygame.Surface:
    return pygame.transform.scale(
        pygame.image.load(
            f"drinks_touch/resources/images/tetris/{sprite_name}.png"
        ).convert_alpha(),
        SPRITE_RESOLUTION * SCALE,
    )
