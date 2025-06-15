from typing import TYPE_CHECKING
import pygame
from pygame import Vector2

from config import Color, Font, SCREEN_WIDTH
from database.models import Account
from screens.tetris.constants import BOARD_WIDTH, SPRITE_RESOLUTION, SCALE, BOARD_HEIGHT
from screens.tetris.shape import Shape
from screens.tetris.utils import darken

if TYPE_CHECKING:
    from screens.tetris.screen import TetrisScreen


class GameInfo:

    def __init__(self, screen: "TetrisScreen"):
        self.t = 0
        self.name_scroll_offset = 0
        # TODO: don't like dependency to parent. Using it for now while refactoring
        self.screen = screen

    def calculate_hash(self):
        return hash((self.name_scroll_offset,))

    def tick(self, dt: float):
        self.t += dt
        self.name_scroll_offset = int(self.t * 3)

    def render(self) -> pygame.Surface:
        w = SCREEN_WIDTH - BOARD_WIDTH * SPRITE_RESOLUTION.x * SCALE
        h = BOARD_HEIGHT * SPRITE_RESOLUTION.y * SCALE
        size = Vector2(w, h)
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
        surface.blit(
            self.render_scoreboard(size.x * 0.9, "GAME", self.screen.scores),
            size.elementwise() * Vector2(0.05, 0.42),
        )
        surface.blit(
            self.render_scoreboard(
                size.x * 0.9, "ALLTIME", self.screen.all_time_scores
            ),
            size.elementwise() * Vector2(0.05, 0.71),
        )

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
        reserve_surface.set_alpha(self.screen.reserve_block_alpha)
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

    def render_scoreboard(
        self, width: float, title: str, scores: list[tuple[Account, int, int]]
    ) -> pygame.Surface:
        size = Vector2(width, 210)
        surface = pygame.Surface(size, pygame.SRCALPHA)

        pygame.draw.rect(
            surface,
            darken(Color.PRIMARY, 0.3),
            (0, 0, size.x, size.y),
            border_radius=10,
        )

        title_font = pygame.font.Font(Font.MONOSPACE.value, 20)
        text_surface = title_font.render(title, 1, Color.BLACK.value)

        label_font = pygame.font.Font(Font.MONOSPACE.value, 11)
        points_label = label_font.render("points", 1, Color.BLACK.value)
        blocks_label = label_font.render("blocks", 1, Color.BLACK.value)

        points_label = pygame.transform.rotate(points_label, -45)
        blocks_label = pygame.transform.rotate(blocks_label, -45)
        surface.blit(points_label, (size.x - 40, 3))
        surface.blit(blocks_label, (size.x - 80, 3))

        surface.blit(text_surface, (5, 10))
        row_font = pygame.font.Font(Font.MONOSPACE.value, 13)

        # only render the scores around the current player, so that they are always visible
        current_player_index = 0
        if self.screen.current_player:
            for i, row in enumerate(scores):
                account, *_ = row
                if account.id == self.screen.current_player.account_id:
                    current_player_index = i
                    break
        scores = scores[max(0, current_player_index - 4) : current_player_index + 10]

        for i, row in enumerate(scores):
            account, blocks, pixels = row
            if (
                self.screen.current_player
                and account.id == self.screen.current_player.account_id
            ):
                text_color = Color.PRIMARY.value
                pygame.draw.rect(
                    surface,
                    darken(self.screen.current_player.color, 0.6),
                    (0, 40 + i * 20, size.x, 20),
                )
            else:
                text_color = Color.BLACK.value

            # scrolling names
            name = account.name
            if len(name) > 6:
                name = " " * 6 + name
                end_offset = len(name)
                start = self.name_scroll_offset % end_offset
                end = start + 6
                name = name[start:end]

            pos = i + 1 + max(0, current_player_index - 4)
            text_surface = row_font.render(
                f"{pos:2}. {name:6} {blocks:4} {pixels:4}", 1, text_color
            )
            surface.blit(text_surface, (5, 40 + i * 20))
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
