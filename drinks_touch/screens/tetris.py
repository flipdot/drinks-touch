import enum
import math
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
    J = 2
    L = 3
    S = 4
    T = 5
    Z = 6
    O = 7  # noqa: E741
    I = 8  # noqa: E741


class Cell(enum.Enum):
    EMPTY = 0
    J = 2
    L = 3
    S = 4
    T = 5
    Z = 6
    O = 7  # noqa: E741
    I_H1 = 8
    I_H2 = 9
    I_H3 = 10
    I_V1 = 11
    I_V2 = 12
    I_V3 = 13
    WALL = 14

    @property
    def sprite(self):
        return {
            Cell.EMPTY: "bg-empty",
            Cell.I_H1: "block-i_h1",
            Cell.I_H2: "block-i_h2",
            Cell.I_H3: "block-i_h3",
            Cell.I_V1: "block-i_v1",
            Cell.I_V2: "block-i_v2",
            Cell.I_V3: "block-i_v3",
            Cell.J: "block-j",
            Cell.L: "block-l",
            Cell.S: "block-s",
            Cell.T: "block-t",
            Cell.Z: "block-z",
            Cell.O: "block-o",
            Cell.WALL: "bg-bricks",
        }[self]


class Shape:
    def __init__(self, block_type: BlockType):
        self.block_type = block_type

        if block_type == BlockType.I:
            self.matrix = [
                [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                [Cell.I_H1, Cell.I_H2, Cell.I_H2, Cell.I_H3],
                [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
            ]
        elif block_type == BlockType.J:
            self.matrix = [
                [Cell.J, Cell.J, Cell.J],
                [Cell.EMPTY, Cell.EMPTY, Cell.J],
            ]
        elif block_type == BlockType.L:
            self.matrix = [
                [Cell.L, Cell.L, Cell.L],
                [Cell.L, Cell.EMPTY, Cell.EMPTY],
            ]
        elif block_type == BlockType.S:
            self.matrix = [
                [Cell.EMPTY, Cell.S, Cell.S],
                [Cell.S, Cell.S, Cell.EMPTY],
            ]
        elif block_type == BlockType.T:
            self.matrix = [
                [Cell.T, Cell.T, Cell.T],
                [Cell.EMPTY, Cell.T, Cell.EMPTY],
            ]
        elif block_type == BlockType.Z:
            self.matrix = [
                [Cell.Z, Cell.Z, Cell.EMPTY],
                [Cell.EMPTY, Cell.Z, Cell.Z],
            ]
        elif block_type == BlockType.O:
            self.matrix = [
                [Cell.O, Cell.O],
                [Cell.O, Cell.O],
            ]

    def rotate(self, clockwise: bool):
        if self.block_type == BlockType.O:
            return
        if self.block_type == BlockType.I:
            is_horizontal = self.matrix[1][1] == Cell.I_H2
            if is_horizontal:
                self.matrix = [
                    [Cell.EMPTY, Cell.I_V1, Cell.EMPTY],
                    [Cell.EMPTY, Cell.I_V2, Cell.EMPTY],
                    [Cell.EMPTY, Cell.I_V2, Cell.EMPTY],
                    [Cell.EMPTY, Cell.I_V3, Cell.EMPTY],
                ]
            else:
                self.matrix = [
                    [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                    [Cell.I_H1, Cell.I_H2, Cell.I_H2, Cell.I_H3],
                    [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
                ]
            return
        if clockwise:
            self.matrix = list(zip(*self.matrix[::-1]))
        else:
            self.matrix = list(zip(*self.matrix))[::-1]

    def render(self, sprites: dict[str, pygame.Surface]) -> pygame.Surface:
        matrix_size = Vector2(len(self.matrix[0]), len(self.matrix))
        size = Vector2(
            matrix_size.elementwise()
            * TetrisScreen.SPRITE_RESOLUTION
            * TetrisScreen.SCALE
        )
        surface = pygame.Surface(size, pygame.SRCALPHA)
        for y, row in enumerate(self.matrix):
            for x, cell in enumerate(row):
                if cell == Cell.EMPTY:
                    continue
                pos = Vector2(x, y)
                surface.blit(
                    sprites[cell.sprite],
                    pos.elementwise()
                    * TetrisScreen.SPRITE_RESOLUTION
                    * TetrisScreen.SCALE,
                )
        return surface


class Direction(enum.Enum):
    LEFT = -1
    RIGHT = 1


class Block:

    def __init__(self, shape: Shape, pos: Vector2, board: list[list[Cell]]):
        self.shape = shape
        self.pos = pos
        self.board = board
        self.locked = False
        self.overlapping = False

    def render(self, sprites: dict[str, pygame.Surface]) -> pygame.Surface:
        return self.shape.render(sprites)

    def move(self, direction: Direction, *, factor=1):
        assert not self.locked, "Block is already locked"
        self.pos.x += direction.value * factor
        if self.collides():
            self.pos.x -= direction.value * factor

    def fall(self):
        """
        Returns False if the block could not fall further
        """
        assert not self.locked, "Block is already locked"
        self.pos.y += 1
        if self.collides():
            self.pos.y -= 1
            return False
        return True

    def lock(self):
        for y, row in enumerate(self.shape.matrix):
            for x, cell in enumerate(row):
                if cell == Cell.EMPTY:
                    continue
                pos = self.pos + Vector2(x, y)
                if self.board[int(pos.y)][int(pos.x)] != Cell.EMPTY:
                    self.overlapping = True
                self.board[int(pos.y)][int(pos.x)] = cell
        self.locked = True

    def rotate(self, clockwise: bool):
        assert not self.locked, "Block is already locked"
        self.shape.rotate(clockwise)
        if self.collides():
            # Try to move the block to the left or right
            for i in range(2):
                self.move(Direction.RIGHT, factor=(i + 1))
                if not self.collides():
                    return
            for i in range(2):
                self.move(Direction.LEFT, factor=(i + 1))
                if not self.collides():
                    return
            # If it still collides, revert rotation
            self.shape.rotate(not clockwise)

    def collides(self) -> bool:
        for y, row in enumerate(self.shape.matrix):
            for x, cell in enumerate(row):
                if cell == Cell.EMPTY:
                    continue
                pos = self.pos + Vector2(x, y)
                if pos.x < 0 or pos.x >= len(self.board[0]) or pos.y >= len(self.board):
                    return True
                if self.board[int(pos.y)][int(pos.x)] != Cell.EMPTY:
                    return True
        return False


class TetrisScreen(Screen):
    nav_bar_visible = False
    SCALE = 1.5
    BOARD_WIDTH = 12
    BOARD_HEIGHT = 32
    SPRITE_RESOLUTION = Vector2(16, 16)

    def __init__(self, account: Account):
        def icon(filename: str):
            return SvgIcon(f"drinks_touch/resources/images/{filename}.svg", height=50)

        super().__init__()
        self.t = 0
        self.last_tick = 0
        self.account = account
        self.sprites = {}
        self.scores: list[tuple[Account, int, int]] = []
        self.score = 0
        self.highscore = 0
        self.reserve_block_type = self.load_reserve_block()
        self.reserve_block_used = False
        self.board = self.load_board()
        self.current_block: Block | None = self.spawn_block()

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

    def spawn_block(self, block_type: None | BlockType = None) -> Block:
        if not block_type:
            block_type = random.choice(list(BlockType))
        return Block(
            shape=Shape(block_type),
            pos=Vector2(self.BOARD_WIDTH // 2 - 1, 0),
            board=self.board,
        )

    def load_board(self) -> list[list[Cell]]:
        empty = [
            [Cell.EMPTY for _ in range(self.BOARD_WIDTH)]
            for _ in range(self.BOARD_HEIGHT)
        ]
        with_walls = [
            [
                (
                    Cell.WALL
                    if x in (0, self.BOARD_WIDTH - 1) or y == self.BOARD_HEIGHT - 1
                    else c
                )
                for x, c in enumerate(r)
            ]
            for y, r in enumerate(empty)
        ]
        return with_walls

    def load_reserve_block(self) -> BlockType:
        # TODO: store this in the database
        return random.choice(list(BlockType))

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

    def use_reserve_block(self):
        if self.reserve_block_used:
            return
        if not self.current_block:
            return
        new_block = self.spawn_block(self.reserve_block_type)
        self.reserve_block_type = self.current_block.shape.block_type
        self.current_block = new_block
        self.reserve_block_used = True

    def tick(self):
        if self.t - self.last_tick < 1:
            return
        self.last_tick = self.t

        if self.current_block is None:
            self.clear_lines()
            self.current_block = self.spawn_block()
            self.reserve_block_used = False
            return

        if not self.current_block.fall():
            self.current_block.lock()
            if self.current_block.overlapping:
                # TODO: game over
                self.board = self.load_board()

            if self.any_row_is_full():
                self.current_block = None
            else:
                self.current_block = self.spawn_block()
                self.reserve_block_used = False
            # self.load_scores()

    def any_row_is_full(self):
        for row in self.board:
            if self.row_is_full(row):
                return True
        return False

    def clear_lines(self):
        for y, row in enumerate(self.board):
            if self.row_is_full(row):
                self.board.pop(y)
                self.board.insert(0, [Cell.EMPTY for _ in range(self.BOARD_WIDTH)])
                self.board[0][-1] = Cell.WALL
                self.board[0][0] = Cell.WALL

    @staticmethod
    def row_is_full(row: list[Cell]) -> bool:
        return all(cell != Cell.EMPTY for cell in row) and not all(
            cell == Cell.WALL for cell in row
        )

    def render(self, dt):
        self.t += dt
        self.tick()
        surface, debug_surface = super().render(dt)

        def blit(x: int, y: int, sprite_name: str):
            v = Vector2(x, y)
            surface.blit(
                self.sprites[sprite_name],
                v.elementwise() * self.SPRITE_RESOLUTION * self.SCALE,
            )

        for y in range(self.BOARD_HEIGHT):
            row_is_full = self.row_is_full(self.board[y])
            for x in range(self.BOARD_WIDTH):
                blit(x, y, self.board[y][x].sprite)
            if row_is_full:
                if math.sin(self.t * 15) < 0:
                    pygame.draw.rect(
                        surface,
                        Color.PRIMARY.value,
                        (
                            self.SPRITE_RESOLUTION.x * self.SCALE,
                            y * self.SPRITE_RESOLUTION.y * self.SCALE,
                            (self.BOARD_WIDTH - 2)
                            * self.SPRITE_RESOLUTION.x
                            * self.SCALE,
                            self.SPRITE_RESOLUTION.y * self.SCALE,
                        ),
                    )

        if self.current_block:
            current_block = self.current_block.render(self.sprites)
            surface.blit(
                current_block,
                self.current_block.pos.elementwise()
                * self.SPRITE_RESOLUTION
                * self.SCALE,
            )

        scoreboard = self.render_gameinfo()
        surface.blit(scoreboard, (config.SCREEN_WIDTH - scoreboard.get_width(), 0))

        return surface, debug_surface

    def render_gameinfo(self) -> pygame.Surface:
        w = (
            config.SCREEN_WIDTH
            - self.BOARD_WIDTH * self.SPRITE_RESOLUTION.x * self.SCALE
        )
        h = self.BOARD_HEIGHT * self.SPRITE_RESOLUTION.y * self.SCALE
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
            border_radius=10,
        )

        title_font = pygame.font.Font(config.Font.MONOSPACE.value, 20)
        title_surface = title_font.render("RESERVE", 1, Color.BLACK.value)
        surface.blit(title_surface, (5, 10))

        reserve_bg_pos = Vector2(30, 40)
        pygame.draw.rect(
            surface,
            Color.PRIMARY.value,
            (*reserve_bg_pos, size.x - 60, 80),
            border_radius=20,
        )

        reserve_shape = Shape(self.reserve_block_type)
        reserve_surface = reserve_shape.render(self.sprites)
        if self.reserve_block_used:
            alpha = 20 + abs(math.sin(self.t * 2)) * 150
        else:
            alpha = 255
        reserve_surface.set_alpha(alpha)
        surface.blit(
            reserve_surface,
            reserve_bg_pos
            + Vector2(
                (size.x - 60 - reserve_surface.get_width()) // 2,
                (80 - reserve_surface.get_height()) // 2,
            ),
        )

        text_font = pygame.font.Font(config.Font.MONOSPACE.value, 16)
        if not self.reserve_block_used:
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
            border_radius=10,
        )

        title_font = pygame.font.Font(config.Font.MONOSPACE.value, 20)
        text_surface = title_font.render("PLAYERS", 1, Color.BLACK.value)

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
        if not self.current_block:
            return
        self.current_block.move(Direction.LEFT)

    def on_rotate_counterclockwise(self):
        if not self.current_block:
            return
        self.current_block.rotate(clockwise=False)

    def on_down(self):
        while self.current_block.fall():
            self.last_tick = self.t

    def on_rotate_clockwise(self):
        if not self.current_block:
            return
        self.current_block.rotate(clockwise=True)

    def on_right(self):
        if not self.current_block:
            return
        self.current_block.move(Direction.RIGHT)

    def event(self, event):

        # check if reserve block was clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            x = self.BOARD_WIDTH * self.SPRITE_RESOLUTION.x * self.SCALE + 10
            y = 10
            w = 180
            h = 160
            if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
                self.use_reserve_block()
                return

        if event.type != pygame.KEYDOWN:
            return super().event(event)

        if event.key == pygame.K_LEFT:
            self.on_left()
        elif event.key == pygame.K_RIGHT:
            self.on_right()
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            self.on_down()
        elif event.key == pygame.K_UP:
            self.on_rotate_clockwise()
        elif event.key == pygame.K_DOWN:
            self.on_rotate_counterclockwise()
        elif event.key == pygame.K_r:
            self.use_reserve_block()
        else:
            return super().event(event)

    def load_sprites(self):
        sprite_names = [
            "bg-empty",
            "bg-bricks",
            "block-o",
            "block-i_h1",
            "block-i_h2",
            "block-i_h3",
            "block-i_v1",
            "block-i_v2",
            "block-i_v3",
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
