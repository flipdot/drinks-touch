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
        self.account = account
        self.sprites = {}
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

    def render(self, dt):
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

        scoreboard_size = size.elementwise() * Vector2((0.9, 0.4))
        surface.blit(
            self.render_scoreboard(scoreboard_size),
            size.elementwise() * Vector2(0.05, 0.01),
        )

        return surface

    def render_scoreboard(self, size: Vector2) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)

        pygame.draw.rect(
            surface,
            Color.PRIMARY.value,
            (0, 10, size.x, size.y),
            width=10,
            border_radius=10,
        )
        # pygame.draw.rect(
        #     surface,
        #     Color.BLACK.value,
        #     (10, 10, size.x - 20, size.y - 20),
        # )

        font = pygame.font.Font(config.Font.MONOSPACE.value, 20)
        text_surface = font.render("SCORE", 1, Color.PRIMARY.value)
        surface.blit(text_surface, (5, 0))
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
