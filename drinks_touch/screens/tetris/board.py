from typing import TYPE_CHECKING

import pygame
from pygame import Vector2

from config import Color
from screens.tetris.constants import SPRITE_RESOLUTION, SCALE, BOARD_WIDTH, BOARD_HEIGHT
from screens.tetris.utils import darken, get_sprite

if TYPE_CHECKING:
    from screens.tetris.screen import TetrisScreen


class Board:

    def __init__(self, screen: "TetrisScreen"):
        # TODO: don't like dependency to parent. Using it for now while refactoring
        self.screen = screen

    def calculate_hash(self):
        # TODO
        return None

    def render(self) -> pygame.Surface:
        surface = pygame.Surface(
            SPRITE_RESOLUTION.elementwise()
            * Vector2(BOARD_WIDTH, BOARD_HEIGHT)
            * SCALE,
        )

        def blit(x: int, y: int, sprite_name: str, account_id: int):
            v = Vector2(x, y)
            if not self.screen.game_started:
                color = (100, 100, 100)
                if sprite_name not in ["bg-empty", "bg-bricks"]:
                    sprite_name = "block-x"
            elif (
                self.screen.current_player
                and self.screen.current_player.account_id == account_id
            ):
                color = self.screen.current_player.color
            else:
                color = Color.PRIMARY.value
            if self.screen.move_ended:
                color = darken(color, 0.3)
            surface.blit(
                get_sprite(sprite_name),
                v.elementwise() * SPRITE_RESOLUTION * SCALE,
            )
            color_square = pygame.Surface(
                SPRITE_RESOLUTION.elementwise() * SCALE,
            )
            color_square.fill(color)
            surface.blit(
                color_square,
                v.elementwise() * SPRITE_RESOLUTION * SCALE,
                special_flags=pygame.BLEND_MULT,
            )
            # pygame.draw.rect(
            #     surface,
            #     (255, 255, 255, 50),
            #     (
            #         v.elementwise() * SPRITE_RESOLUTION * SCALE,
            #         SPRITE_RESOLUTION * SCALE,
            #     ),
            # )

        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.screen.loading:
                    blit(x, y, "bg-bricks", -1)
                else:
                    blit(
                        x,
                        y,
                        self.screen.board[y][x].type.sprite,
                        self.screen.board[y][x].account_id,
                    )
            row_is_full = not self.screen.loading and self.screen.row_is_full(
                self.screen.board[y]
            )
            if row_is_full and not self.screen.hide_full_row:
                pygame.draw.rect(
                    surface,
                    Color.PRIMARY.value,
                    (
                        SPRITE_RESOLUTION.x * SCALE,
                        y * SPRITE_RESOLUTION.y * SCALE,
                        (BOARD_WIDTH - 2) * SPRITE_RESOLUTION.x * SCALE,
                        SPRITE_RESOLUTION.y * SCALE,
                    ),
                )

        if self.screen.current_block:
            current_block_surface = self.screen.current_block.render()
            shadow_surface = current_block_surface.copy()
            shadow_surface.fill((0, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
            shadow_pos = self.screen.current_block.shadow_pos
            surface.blit(
                shadow_surface,
                shadow_pos.elementwise() * SPRITE_RESOLUTION * SCALE,
            )

            surface.blit(
                current_block_surface,
                self.screen.current_block.pos.elementwise() * SPRITE_RESOLUTION * SCALE,
            )

        return surface
