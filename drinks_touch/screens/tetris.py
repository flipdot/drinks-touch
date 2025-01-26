import enum
import random

import pygame
from pygame import Vector2, Vector3

import config
from config import Color
from database.models import Account
from elements import Button, SvgIcon
from elements.hbox import HBox
from screens.screen import Screen


def darken(color: Color, factor: float) -> Vector3:
    return Vector3(*color.value[:3]) * (1 - factor)


def lighten(color: Color, factor: float) -> Vector3:
    return Vector3(*color.value[:3]) * (1 - factor) + Vector3(255, 255, 255) * factor


class BlockType(enum.Enum):
    I = 0  # noqa: E741
    J = 1
    L = 2
    S = 3
    T = 4
    Z = 5
    O = 6  # noqa: E741


class TetrisScreen(Screen):
    nav_bar_visible = False
    SCALE = 1.5
    BOARD_WIDTH = 10
    BOARD_HEIGHT = 30
    SPRITE_RESOLUTION = Vector2(16, 16)

    def __init__(self, account: Account):
        def icon(filename: str):
            return SvgIcon(f"drinks_touch/resources/images/{filename}.svg", height=50)

        super().__init__()
        self.t = 0
        self.account = account
        self.sprites = {}
        self.scores: list[tuple[Account, int, int]] = []
        self.score = 0
        self.highscore = 0
        self.reserve_block = random.choice(list(BlockType))

        self.objects = [
            HBox(
                [
                    Button(
                        inner=icon("arrow-left"),
                        on_click=self.on_left,
                    ),
                    Button(
                        inner=icon("rotate-counterclockwise"),
                        on_click=self.on_rotate_counterclockwise,
                    ),
                    Button(
                        inner=icon("arrow-down-long"),
                        on_click=self.on_down,
                    ),
                    Button(
                        inner=icon("rotate-clockwise"),
                        on_click=self.on_rotate_clockwise,
                    ),
                    Button(
                        inner=icon("arrow-right"),
                        on_click=self.on_right,
                    ),
                ],
                pos=(25, config.SCREEN_HEIGHT),
                align_bottom=True,
                padding=10,
                gap=20,
            )
        ]
        self.load_scores()

    def load_scores(self):
        # dummy values for now as long as we don't have a database table
        import random

        self.scores = []
        for i, account in enumerate(Account.query.limit(20)):
            lines = random.randint(1, 10)
            blocks = random.randint(1, 100)
            self.scores.append((account, lines, blocks))
        self.score = random.randint(1, 1000)
        self.highscore = self.score + random.randint(1, 1000)

    def render(self, dt):
        self.t += dt
        surface, debug_surface = super().render(dt)

        def blit(x: int, y: int, sprite_name: str):
            x += 1
            v = Vector2(x, self.BOARD_HEIGHT - y)
            surface.blit(
                self.sprites[sprite_name],
                v.elementwise() * self.SPRITE_RESOLUTION * self.SCALE,
            )

        v = Vector2(self.BOARD_WIDTH, self.BOARD_HEIGHT) + Vector2(2, 2)
        pygame.draw.rect(
            surface,
            Color.PRIMARY.value,
            (
                0,
                0,
                *(v.elementwise() * self.SPRITE_RESOLUTION * self.SCALE),
            ),
        )
        for x in range(-1, self.BOARD_WIDTH + 1):
            for y in range(-1, self.BOARD_HEIGHT + 1):
                if x < 0 or x >= self.BOARD_WIDTH or y < 0 or y >= self.BOARD_HEIGHT:
                    blit(x, y, "bg-bricks")
                if y == 0:
                    if x == 0:
                        blit(x, y, "block-i")
                    elif x == 1:
                        blit(x, y, "block-j")
                    elif x == 2:
                        blit(x, y, "block-l")
                    elif x == 3:
                        blit(x, y, "block-s")
                    elif x == 4:
                        blit(x, y, "block-t")
                    elif x == 5:
                        blit(x, y, "block-z")
                    elif x == 6:
                        blit(x, y, "block-o")
        surface.blit(self.sprites["bg-bricks"], (0, 0))
        scoreboard = self.render_gameinfo()
        surface.blit(scoreboard, (config.SCREEN_WIDTH - scoreboard.get_width(), 0))
        return surface, debug_surface

    def render_gameinfo(self) -> pygame.Surface:
        w = (
            config.SCREEN_WIDTH
            - (self.BOARD_WIDTH + 2) * self.SPRITE_RESOLUTION.x * self.SCALE
        )
        h = (self.BOARD_HEIGHT + 2) * self.SPRITE_RESOLUTION.y * self.SCALE
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
            self.render_scoreboard(size.x * 0.9),
            size.elementwise() * Vector2(0.05, 0.43),
        )

        return surface

    def render_reserve_block(self, width: float) -> pygame.Surface:
        size = Vector2(width, 150)
        surface = pygame.Surface(size, pygame.SRCALPHA)

        pygame.draw.rect(
            surface,
            darken(Color.PRIMARY, 0.3),
            (0, 0, size.x, size.y),
        )

        title_font = pygame.font.Font(config.Font.MONOSPACE.value, 20)
        title_surface = title_font.render("RESERVE", 1, Color.BLACK.value)
        surface.blit(title_surface, (5, 10))

        pygame.draw.rect(
            surface,
            Color.PRIMARY.value,
            (20, 40, size.x - 40, 80),
        )

        text_font = pygame.font.Font(config.Font.MONOSPACE.value, 16)
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
        )

        title_font = pygame.font.Font(config.Font.MONOSPACE.value, 20)
        title_score_surface = title_font.render("SCORE", 1, Color.BLACK.value)
        title_highscore_surface = title_font.render("HIGHSCORE", 1, Color.BLACK.value)
        score_font = pygame.font.Font(config.Font.MONOSPACE.value, 16)

        score_surface = score_font.render(str(self.score), 1, Color.BLACK.value)
        highscore_surface = score_font.render(str(self.highscore), 1, Color.BLACK.value)

        surface.blit(title_score_surface, (5, 10))
        surface.blit(score_surface, (size.x - score_surface.get_width() - 5, 35))
        surface.blit(title_highscore_surface, (5, 60))
        surface.blit(
            highscore_surface, (size.x - highscore_surface.get_width() - 5, 85)
        )
        return surface

    def render_scoreboard(self, width: float) -> pygame.Surface:
        size = Vector2(width, 430)
        surface = pygame.Surface(size, pygame.SRCALPHA)

        pygame.draw.rect(
            surface,
            darken(Color.PRIMARY, 0.3),
            (0, 0, size.x, size.y),
        )

        title_font = pygame.font.Font(config.Font.MONOSPACE.value, 20)
        text_surface = title_font.render("SCORES", 1, Color.BLACK.value)

        label_font = pygame.font.Font(config.Font.MONOSPACE.value, 11)
        lines_label = label_font.render("lines", 1, Color.BLACK.value)
        blocks_label = label_font.render("blocks", 1, Color.BLACK.value)

        lines_label = pygame.transform.rotate(lines_label, -45)
        blocks_label = pygame.transform.rotate(blocks_label, -45)
        surface.blit(lines_label, (size.x - 40, 3))
        surface.blit(blocks_label, (size.x - 80, 3))

        surface.blit(text_surface, (5, 10))
        row_font = pygame.font.Font(config.Font.MONOSPACE.value, 13)
        for i, row in enumerate(self.scores):
            account, lines, blocks = row
            if account == self.account:
                text_color = Color.PRIMARY.value
                pygame.draw.rect(
                    surface,
                    Color.BLACK.value,
                    (0, 40 + i * 20, size.x, 20),
                )
            else:
                text_color = Color.BLACK.value

            # scrolling names
            name = account.name
            if len(name) > 6:
                name = " " * 6 + name
                end_offset = len(name)
                start = int(self.t * 5) % end_offset
                end = start + 6
                name = name[start:end]

            text_surface = row_font.render(
                f"{i+1:2}. {name:6} {blocks:4} {lines:4}", 1, text_color
            )
            surface.blit(text_surface, (5, 40 + i * 20))
        return surface

    def on_start(self, *args, **kwargs):
        self.load_sprites()

    def on_left(self):
        pass

    def on_rotate_counterclockwise(self):
        pass

    def on_down(self):
        pass

    def on_rotate_clockwise(self):
        pass

    def on_right(self):
        pass

    def load_sprites(self):
        sprite_names = [
            "bg-bricks",
            "block-o",
            "block-i",
            "block-j",
            "block-l",
            "block-s",
            "block-t",
            "block-z",
        ]

        self.sprites = {
            x: pygame.transform.scale(
                pygame.image.load(
                    f"drinks_touch/resources/images/tetris/{x}.png"
                ).convert_alpha(),
                self.SPRITE_RESOLUTION * self.SCALE,
            )
            for x in sprite_names
        }
