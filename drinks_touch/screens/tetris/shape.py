import pygame
from pygame import Vector2

from screens.tetris.block import BlockType
from screens.tetris.cell import CellType
from screens.tetris.constants import SPRITE_RESOLUTION, SCALE
from screens.tetris.utils import get_sprite


class Shape:
    def __init__(self, block_type: BlockType):
        self.block_type = block_type

        if block_type == BlockType.I:
            self.matrix = [
                [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
                [CellType.I_H1, CellType.I_H2, CellType.I_H2, CellType.I_H3],
                [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
            ]
        elif block_type == BlockType.J:
            self.matrix = [
                [CellType.J, CellType.J, CellType.J],
                [CellType.EMPTY, CellType.EMPTY, CellType.J],
            ]
        elif block_type == BlockType.L:
            self.matrix = [
                [CellType.L, CellType.L, CellType.L],
                [CellType.L, CellType.EMPTY, CellType.EMPTY],
            ]
        elif block_type == BlockType.S:
            self.matrix = [
                [CellType.EMPTY, CellType.S, CellType.S],
                [CellType.S, CellType.S, CellType.EMPTY],
            ]
        elif block_type == BlockType.T:
            self.matrix = [
                [CellType.T, CellType.T, CellType.T],
                [CellType.EMPTY, CellType.T, CellType.EMPTY],
            ]
        elif block_type == BlockType.Z:
            self.matrix = [
                [CellType.Z, CellType.Z, CellType.EMPTY],
                [CellType.EMPTY, CellType.Z, CellType.Z],
            ]
        elif block_type == BlockType.O:
            self.matrix = [
                [CellType.O, CellType.O],
                [CellType.O, CellType.O],
            ]
        else:
            self.matrix = [
                [CellType.EMPTY],
            ]

    def calculate_hash(self) -> int:
        return hash(
            (
                self.block_type,
                tuple(tuple(row) for row in self.matrix),
            )
        )

    def rotate(self, clockwise: bool):
        if self.block_type == BlockType.O:
            return
        if self.block_type == BlockType.I:
            is_horizontal = self.matrix[1][1] == CellType.I_H2
            if is_horizontal:
                self.matrix = [
                    [CellType.EMPTY, CellType.I_V1, CellType.EMPTY],
                    [CellType.EMPTY, CellType.I_V2, CellType.EMPTY],
                    [CellType.EMPTY, CellType.I_V2, CellType.EMPTY],
                    [CellType.EMPTY, CellType.I_V3, CellType.EMPTY],
                ]
            else:
                self.matrix = [
                    [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
                    [CellType.I_H1, CellType.I_H2, CellType.I_H2, CellType.I_H3],
                    [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
                ]
            return
        if clockwise:
            self.matrix = list(zip(*self.matrix[::-1]))
        else:
            self.matrix = list(zip(*self.matrix))[::-1]

    def render(self, color: tuple[int, int, int]) -> pygame.Surface:
        matrix_size = Vector2(len(self.matrix[0]), len(self.matrix))
        size = Vector2(matrix_size.elementwise() * SPRITE_RESOLUTION * SCALE)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        for y, row in enumerate(self.matrix):
            for x, cell in enumerate(row):
                if cell == CellType.EMPTY:
                    continue
                pos = Vector2(x, y)
                surface.blit(
                    get_sprite(cell.sprite),
                    pos.elementwise() * SPRITE_RESOLUTION * SCALE,
                )
                color_square = pygame.Surface(
                    SPRITE_RESOLUTION.elementwise() * SCALE,
                )
                color_square.fill(color)
                surface.blit(
                    color_square,
                    pos.elementwise() * SPRITE_RESOLUTION * SCALE,
                    special_flags=pygame.BLEND_MULT,
                )
        return surface
