import enum
import logging

import pygame
from pygame import Vector2

from screens.tetris.cell import Cell, CellType
from screens.tetris.player import Player

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from screens.tetris.shape import Shape


logger = logging.getLogger(__name__)


class Direction(enum.Enum):
    LEFT = -1
    RIGHT = 1


class BlockType(enum.IntEnum):
    J = 2
    L = 3
    S = 4
    T = 5
    Z = 6
    O = 7  # noqa: E741
    I = 8  # noqa: E741


class Block:

    def __init__(
        self, shape: "Shape", pos: Vector2, board: list[list[Cell]], player: Player
    ):
        self.shape = shape
        self.pos = pos
        self.board = board
        self.locked = False
        self.overlapping = False
        self.player = player
        self.dirty = True
        self.last_hash = 0
        self.surface: pygame.Surface | None = None

    def calculate_hash(self) -> int:
        return hash(
            (
                self.shape.calculate_hash(),
                self.pos.x,
                self.pos.y,
                self.locked,
                self.overlapping,
                self.player.account_id,
            )
        )

    def _render(self) -> pygame.Surface:
        color = self.player.color
        return self.shape.render(color)

    def render(self) -> pygame.Surface:
        if self.surface is None or self.last_hash != self.calculate_hash():
            self.last_hash = self.calculate_hash()
            self.dirty = True
        if self.dirty:
            self.surface = self._render()
            self.dirty = False
        return self.surface

    def move(self, direction: Direction, *, factor=1):
        if self.locked:
            logger.warning("Block is already locked")
            return
        self.pos.x += direction.value * factor
        if self.collides():
            self.pos.x -= direction.value * factor

    def fall(self):
        """
        Returns False if the block could not fall further
        """
        if self.locked:
            logger.warning("Block is already locked")
            return
        self.pos.y += 1
        if self.collides():
            self.pos.y -= 1
            return False
        return True

    def lock(self):
        for y, row in enumerate(self.shape.matrix):
            for x, celltype in enumerate(row):
                if celltype == CellType.EMPTY:
                    continue
                pos = self.pos + Vector2(x, y)
                if self.board[int(pos.y)][int(pos.x)].type != CellType.EMPTY:
                    self.overlapping = True
                self.board[int(pos.y)][int(pos.x)] = Cell(
                    celltype, self.player.account_id
                )
        self.locked = True

    def rotate(self, clockwise: bool) -> bool:
        if self.locked:
            logger.warning("Block is already locked")
            return
        self.shape.rotate(clockwise)
        if not self.collides():
            return True
        # Try to move the block to the left or right
        for i in range(2):
            self.move(Direction.RIGHT, factor=(i + 1))
            if not self.collides():
                return True
        for i in range(2):
            self.move(Direction.LEFT, factor=(i + 1))
            if not self.collides():
                return True
        # If it still collides, revert rotation
        self.shape.rotate(not clockwise)
        return False

    def collides(self, p: None | Vector2 = None) -> bool:
        if p is None:
            p = self.pos
        for y, row in enumerate(self.shape.matrix):
            for x, cell in enumerate(row):
                if cell == CellType.EMPTY:
                    continue
                pos = p + Vector2(x, y)
                if pos.x < 0 or pos.x >= len(self.board[0]) or pos.y >= len(self.board):
                    return True
                if self.board[int(pos.y)][int(pos.x)].type != CellType.EMPTY:
                    return True
        return False

    @property
    def shadow_pos(self) -> Vector2:
        pos = self.pos.copy()
        while not self.collides(pos):
            pos.y += 1
        pos.y -= 1
        return pos
