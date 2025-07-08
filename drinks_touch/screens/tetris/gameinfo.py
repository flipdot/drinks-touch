import math
from typing import TYPE_CHECKING
import pygame
from pygame import Vector2

from config import Color, Font, SCREEN_WIDTH
from screens.tetris.constants import BOARD_WIDTH, SPRITE_RESOLUTION, SCALE, BOARD_HEIGHT
from screens.tetris.scoreboard import Scoreboard
from screens.tetris.shape import Shape
from screens.tetris.utils import darken

if TYPE_CHECKING:
    from screens.tetris.screen import TetrisScreen


class GameInfo:

    def __init__(
        self,
        screen: "TetrisScreen",
        scores: list[tuple[int, str, int, int]],
        all_time_scores: list[tuple[int, str, int, int]],
    ):
        self.last_hash = 0
        self.dirty = True
        self.surface: pygame.Surface | None = None
        self.t = 0
        self.reserve_block_alpha = 255
        self.width = SCREEN_WIDTH - BOARD_WIDTH * SPRITE_RESOLUTION.x * SCALE
        self.height = BOARD_HEIGHT * SPRITE_RESOLUTION.y * SCALE
        self.scoreboard = Scoreboard(
            screen, width=self.width * 0.9, title="GAME", scores=scores
        )
        self.all_time_scoreboard = Scoreboard(
            screen, width=self.width * 0.9, title="ALLTIME", scores=all_time_scores
        )
        # TODO: don't like dependency to parent. Using it for now while refactoring
        self.screen = screen

    def calculate_hash(self):
        return hash(
            (
                self.reserve_block_alpha,
                self.width,
                self.height,
                self.scoreboard.calculate_hash(),
                self.all_time_scoreboard.calculate_hash(),
            )
        )

    def render(self) -> pygame.Surface:
        """
        Caches the result of the internal `_render` method
        """
        if self.last_hash != (new_hash := self.calculate_hash()):
            self.dirty = True
            self.last_hash = new_hash
        if self.dirty:
            self.surface = self._render()
            self.dirty = False
        return self.surface

    def tick(self, dt: float):
        self.t += dt
        self.scoreboard.tick(dt)
        self.all_time_scoreboard.tick(dt)
        if self.screen.reserve_block_used:
            self.reserve_block_alpha = int(20 + abs(math.sin(self.t * 2)) * 150)
        else:
            self.reserve_block_alpha = 255

    def _render(self) -> pygame.Surface:
        size = Vector2(self.width, self.height)
        surface = pygame.Surface(size)
        surface.fill(darken(Color.PRIMARY, 0.8))

        surface.blit(
            self.render_reserve_block(size.x * 0.9),
            size.elementwise() * Vector2(0.05, 0.02),
        )
        surface.blit(
            self.render_score(size.x * 0.9),
            size.elementwise() * Vector2(0.05, 0.25),
        )
        surface.blit(self.scoreboard.render(), size.elementwise() * Vector2(0.05, 0.42))
        surface.blit(
            self.all_time_scoreboard.render(), size.elementwise() * Vector2(0.05, 0.71)
        )
        # surface.blit(
        #     self.render_scoreboard(size.x * 0.9, "GAME", self.screen.scores),
        #     size.elementwise() * Vector2(0.05, 0.42),
        # )
        # surface.blit(
        #     self.render_scoreboard(
        #         size.x * 0.9, "ALLTIME", self.screen.all_time_scores
        #     ),
        #     size.elementwise() * Vector2(0.05, 0.71),
        # )

        return surface

    def render_reserve_block(self, width: float) -> pygame.Surface:
        size = Vector2(width, 150)
        surface = pygame.Surface(size, pygame.SRCALPHA)

        pygame.draw.rect(
            surface,
            darken(Color.PRIMARY, 0.3),
            (0, 0, size.x, size.y),
            border_radius=10,
        )

        title_font = pygame.font.Font(Font.MONOSPACE.value, 20)
        title_surface = title_font.render("RESERVE", 1, Color.BLACK.value)
        surface.blit(title_surface, (5, 10))

        reserve_bg_pos = Vector2(30, 40)
        pygame.draw.rect(
            surface,
            Color.PRIMARY.value,
            (*reserve_bg_pos, size.x - 60, 80),
            border_radius=20,
        )

        reserve_shape = Shape(self.screen.reserve_block_type)
        reserve_surface = reserve_shape.render(Color.PRIMARY.value)
        reserve_surface.set_alpha(self.reserve_block_alpha)
        surface.blit(
            reserve_surface,
            reserve_bg_pos
            + Vector2(
                (size.x - 60 - reserve_surface.get_width()) // 2,
                (80 - reserve_surface.get_height()) // 2,
            ),
        )

        text_font = pygame.font.Font(Font.MONOSPACE.value, 16)
        if not self.screen.reserve_block_used:
            text_surface = text_font.render("Tauschen", 1, Color.BLACK.value)
            surface.blit(text_surface, (45, 125))
        return surface

    def render_score(self, width: float) -> pygame.Surface:
        size = Vector2(width, 110)
        surface = pygame.Surface(size, pygame.SRCALPHA)

        pygame.draw.rect(
            surface,
            darken(Color.PRIMARY, 0.3),
            (0, 0, size.x, size.y),
            border_radius=10,
        )

        font = pygame.font.Font(Font.MONOSPACE.value, 20)
        title_level_surface = font.render("LEVEL", 1, Color.BLACK.value)
        title_lines_surface = font.render("LINES", 1, Color.BLACK.value)
        score_surface = font.render(
            f"SCORE {self.screen.score:8}", 1, Color.BLACK.value
        )
        highscore_surface = font.render(
            f"HIGHS. {self.screen.highscore:7}", 1, Color.BLACK.value
        )

        level_surface = font.render(f"{self.screen.level:5}", 1, Color.BLACK.value)
        lines_surface = font.render(str(self.screen.lines), 1, Color.BLACK.value)

        surface.blit(title_level_surface, (5, 5))
        surface.blit(
            title_lines_surface, (width - title_lines_surface.get_width() - 5, 5)
        )
        surface.blit(level_surface, (5, 25))
        surface.blit(lines_surface, (width - lines_surface.get_width() - 5, 25))
        surface.blit(score_surface, (5, 60))
        surface.blit(highscore_surface, (5, 85))
        # surface.blit(title_highscore_surface, (5, 65))
        # surface.blit(
        #     highscore_surface, (size.x - highscore_surface.get_width() - 5, 85)
        # )
        return surface
