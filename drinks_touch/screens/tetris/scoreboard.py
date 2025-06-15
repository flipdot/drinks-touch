import pygame
from pygame import Vector2

from config import Color, Font
from database.models import Account
from screens.tetris.utils import darken

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from screens.tetris.screen import TetrisScreen


class Scoreboard:

    def __init__(
        self,
        screen: "TetrisScreen",
        width: float,
        title: str,
        scores: list[tuple[Account, int, int]],
    ):
        self.t = 0
        self.last_hash = 0
        self.dirty = True
        self.surface: pygame.Surface | None = None
        self.name_scroll_offset = 0
        self.screen = screen
        self.width = width
        self.title = title
        self.scores = scores

    def calculate_hash(self):
        return hash((self.name_scroll_offset, self.width, self.title))

    def tick(self, dt: float):
        self.t += dt
        self.name_scroll_offset = int(self.t * 3)

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

    def _render(self) -> pygame.Surface:
        # self, width: float, title: str, scores: list[tuple[Account, int, int]]
        size = Vector2(self.width, 210)
        surface = pygame.Surface(size, pygame.SRCALPHA)

        pygame.draw.rect(
            surface,
            darken(Color.PRIMARY, 0.3),
            (0, 0, size.x, size.y),
            border_radius=10,
        )

        title_font = pygame.font.Font(Font.MONOSPACE.value, 20)
        text_surface = title_font.render(self.title, 1, Color.BLACK.value)

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
            for i, row in enumerate(self.scores):
                account, *_ = row
                if account.id == self.screen.current_player.account_id:
                    current_player_index = i
                    break
        scores = self.scores[
            max(0, current_player_index - 4) : current_player_index + 10
        ]

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
