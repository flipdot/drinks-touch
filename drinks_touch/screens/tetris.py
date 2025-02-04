import enum
import functools
import json
import logging
import math
import random

import pygame
from pygame import Vector2, Vector3
from pygame.mixer import Sound

import config
from config import Color
from database.models import Account, TetrisPlayer, TetrisGame
from database.storage import Session
from elements import Button, SvgIcon, Progress
from elements.hbox import HBox
from screens.screen import Screen


logger = logging.getLogger(__name__)


def darken(color: Color | tuple[int, int, int], factor: float) -> Vector3:
    if isinstance(color, Color):
        v = color.value[:3]
    else:
        v = color
    return Vector3(*v) * (1 - factor)


def lighten(color: Color, factor: float) -> Vector3:
    return Vector3(*color.value[:3]) * (1 - factor) + Vector3(255, 255, 255) * factor


class TetrisJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Cell):
            return [o.type, o.account_id]
        return super().default(o)


# class TetrisJSONDecoder(json.JSONDecoder):
#     def __init__(self, *args, **kwargs):
#         super().__init__(object_hook=self.object_hook, *args, **kwargs)
#
#     def object_hook(self, o):
#         if len(o) == 2:
#             return Cell(CellType(o[0]), o[1])
#         return o


class BlockType(enum.IntEnum):
    J = 2
    L = 3
    S = 4
    T = 5
    Z = 6
    O = 7  # noqa: E741
    I = 8  # noqa: E741


class CellType(enum.IntEnum):
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
            CellType.EMPTY: "bg-empty",
            CellType.I_H1: "block-i_h1",
            CellType.I_H2: "block-i_h2",
            CellType.I_H3: "block-i_h3",
            CellType.I_V1: "block-i_v1",
            CellType.I_V2: "block-i_v2",
            CellType.I_V3: "block-i_v3",
            CellType.J: "block-j",
            CellType.L: "block-l",
            CellType.S: "block-s",
            CellType.T: "block-t",
            CellType.Z: "block-z",
            CellType.O: "block-o",
            CellType.WALL: "bg-bricks",
        }[self]


class Cell:

    def __init__(self, celltype: CellType = CellType.EMPTY, account_id: int = -1):
        self.type = celltype
        self.account_id = account_id


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

    def render(
        self, sprites: dict[str, pygame.Surface], color: tuple[int, int, int]
    ) -> pygame.Surface:
        matrix_size = Vector2(len(self.matrix[0]), len(self.matrix))
        size = Vector2(
            matrix_size.elementwise()
            * TetrisScreen.SPRITE_RESOLUTION
            * TetrisScreen.SCALE
        )
        surface = pygame.Surface(size, pygame.SRCALPHA)
        for y, row in enumerate(self.matrix):
            for x, cell in enumerate(row):
                if cell == CellType.EMPTY:
                    continue
                pos = Vector2(x, y)
                surface.blit(
                    sprites[cell.sprite],
                    pos.elementwise()
                    * TetrisScreen.SPRITE_RESOLUTION
                    * TetrisScreen.SCALE,
                )
                color_square = pygame.Surface(
                    TetrisScreen.SPRITE_RESOLUTION.elementwise() * TetrisScreen.SCALE,
                )
                color_square.fill(color)
                surface.blit(
                    color_square,
                    pos.elementwise()
                    * TetrisScreen.SPRITE_RESOLUTION
                    * TetrisScreen.SCALE,
                    special_flags=pygame.BLEND_MULT,
                )
        return surface


class Direction(enum.Enum):
    LEFT = -1
    RIGHT = 1


class Player:

    def __init__(self, account: Account):
        player = TetrisPlayer.query.filter_by(account_id=account.id).first()
        if player is None:
            player = TetrisPlayer(
                account_id=account.id,
                score=0,
                blocks=0,
                lines=0,
                alltime_score=0,
                alltime_blocks=0,
                alltime_lines=0,
            )
            Session.add(player)
            Session.commit()
        self.score = player.score
        self.blocks = player.blocks
        self.lines = player.lines
        self.alltime_score = player.alltime_score
        self.alltime_blocks = player.alltime_blocks
        self.alltime_lines = player.alltime_lines
        self.account_id = account.id
        self.color = (0, 255, 0)  # TODO: Allow each player to configure their color


class Block:

    def __init__(
        self, shape: Shape, pos: Vector2, board: list[list[Cell]], player: Player
    ):
        self.shape = shape
        self.pos = pos
        self.board = board
        self.locked = False
        self.overlapping = False
        self.player = player

    def render(self, sprites: dict[str, pygame.Surface]) -> pygame.Surface:
        color = self.player.color
        return self.shape.render(sprites, color)

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


class TetrisScreen(Screen):
    nav_bar_visible = False
    SCALE = 1.5
    BOARD_WIDTH = 12
    BOARD_HEIGHT = 32
    SPRITE_RESOLUTION = Vector2(16, 16)
    background_color = darken(Color.PRIMARY, 0.8)

    def __init__(self, account: Account):
        def icon(filename: str):
            return SvgIcon(f"drinks_touch/resources/images/{filename}.svg", height=50)

        super().__init__()

        # if not TetrisPlayer.query.filter_by(account_id=account.id).first():
        #     Session.add(TetrisPlayer(
        #         account_id=account.id,
        #         score=0,
        #         blocks=0,
        #         lines=0,
        #         alltime_score=0,
        #         alltime_blocks=0,
        #         alltime_lines=0,
        #     ))
        #     Session.commit()
        if not TetrisGame.query.first():
            Session.add(
                TetrisGame(
                    score=0,
                    highscore=0,
                    level=0,
                    lines=0,
                    next_blocks=[],
                    board=[],
                    reserve_block=random.choice(list(BlockType)),
                )
            )
            Session.commit()

        self.t = 0
        self.last_tick = 0
        self.account = account
        self.sprites = self.load_sprites()
        self.scores: list[tuple[Account, int, int]] = []
        self.all_time_scores: list[tuple[Account, int, int]] = []
        self.score = 0
        self.highscore = 0
        self.lines = 0
        self.reserve_block_type = self.load_reserve_block()
        self.reserve_block_used = False
        self.board = self.load_board()
        self.level = self.load_level()
        self.next_blocks: list[BlockType] = self.load_next_blocks()
        self.current_player = Player(account)
        self.current_block: Block | None = self.spawn_block()
        self.game_over = False
        self.move_ended = False
        self.sounds = {
            name: Sound(f"drinks_touch/resources/sounds/tetris/{name}.wav")
            for name in [
                "move-block",
                "line-clear",
                "4-line-clear",
                "lock-block",
                "rotate-block",
                "use-reserve",
                "block-fall",
                "block-to-bottom",
                "game-over",
            ]
        }

        self.objects = [
            HBox(
                [
                    Button(
                        inner=icon("arrow-left"),
                        on_click=self.on_left,
                    ),
                    Button(
                        inner=icon("rotate-counterclockwise"),
                        on_click=functools.partial(self.on_rotate, clockwise=False),
                    ),
                    Button(
                        inner=icon("arrow-down-long"),
                        on_click=self.on_down,
                    ),
                    Button(
                        inner=icon("rotate-clockwise"),
                        on_click=functools.partial(self.on_rotate, clockwise=True),
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
            block_type = self.draw_block()
        return Block(
            shape=Shape(block_type),
            pos=Vector2(self.BOARD_WIDTH // 2 - 1, 0),
            board=self.board,
            player=self.current_player,
        )

    def load_level(self) -> int:
        game = TetrisGame.query.first()
        if game.level:
            return game.level
        return 0

    def load_next_blocks(self) -> list[BlockType]:
        game = TetrisGame.query.first()
        if game.next_blocks:
            return [BlockType(b) for b in game.next_blocks]
        return self.generate_block_bag()

    def generate_block_bag(self) -> list[BlockType]:
        all_blocks = list(BlockType)
        random.shuffle(all_blocks)
        return all_blocks

    def load_board(self) -> list[list[Cell]]:
        game = TetrisGame.query.first()
        if game.board:
            # convert json to Cell with CellType enum
            return [[Cell(CellType(c), p) for c, p in row] for row in game.board]
        return self.generate_empty_board()

    def generate_empty_board(self) -> list[list[Cell]]:
        empty = [
            [Cell() for _ in range(self.BOARD_WIDTH)] for _ in range(self.BOARD_HEIGHT)
        ]
        with_walls = [
            [
                (
                    Cell(CellType.WALL)
                    if x in (0, self.BOARD_WIDTH - 1) or y == self.BOARD_HEIGHT - 1
                    else c
                )
                for x, c in enumerate(r)
            ]
            for y, r in enumerate(empty)
        ]
        return with_walls

    def load_reserve_block(self) -> BlockType:
        return TetrisGame.query.first().reserve_block

    def load_scores(self):
        query = Session().query(TetrisPlayer, Account).join(Account)
        self.scores = [
            (account, score.lines, score.blocks)
            for score, account in query.order_by(
                TetrisPlayer.lines.desc(), TetrisPlayer.blocks.desc()
            )
            # .limit(10)
            .all()
            if score.blocks > 0
        ]
        self.all_time_scores = [
            (account, score.alltime_lines, score.alltime_blocks)
            for score, account in query.order_by(
                TetrisPlayer.alltime_lines.desc(), TetrisPlayer.alltime_blocks.desc()
            )
            # .limit(10)
            .all()
        ]
        game = TetrisGame.query.first()
        self.score = game.score
        self.highscore = game.highscore
        self.level = game.level
        self.lines = game.lines
        # self.next_blocks = game.next_blocks
        # self.board = game.board

    def draw_block(self, pop: bool = True) -> BlockType:
        assert len(self.next_blocks) > 0, "No more blocks to draw"
        if pop:
            block = self.next_blocks.pop()
            if len(self.next_blocks) == 0:
                self.next_blocks = self.generate_block_bag()
            return block
        return self.next_blocks[-1]

    def use_reserve_block(self):
        if (
            self.game_over
            or self.move_ended
            or not self.current_block
            or self.current_block.locked
            or self.reserve_block_used
        ):
            return
        new_block = self.spawn_block(self.reserve_block_type)
        self.reserve_block_type = self.current_block.shape.block_type
        self.current_block = new_block
        self.reserve_block_used = True
        self.sounds["use-reserve"].play()

    def tick(self):

        if self.game_over:
            if self.t - self.last_tick < 1.5:
                return
            self.last_tick = self.t
            # cycle through the highscores by switching the current player
            i = 0
            for i, (account, _, _) in enumerate(self.scores):
                if account.id == self.account.id:
                    break
            i -= 1
            if i < 0:
                i = len(self.scores) - 1
            self.account = self.scores[i][0]
            self.current_player = Player(self.scores[i][0])

            return

        if self.move_ended:
            return

        if not self.current_block:
            if self.t - self.last_tick < 1.5:
                return
            self.last_tick = self.t
            self.settle_block()
            return

        time_per_block_fall = 1 / (self.level + 1)
        if self.t - self.last_tick < time_per_block_fall:
            return
        self.last_tick = self.t

        if not self.current_block.fall():
            self.current_block.lock()
            self.sounds["lock-block"].play()
            if self.current_block.overlapping:
                self.end_game()
                return

            if n := self.count_full_rows():
                self.current_block = None
                if n == 4:
                    self.sounds["4-line-clear"].play()
                else:
                    self.sounds["line-clear"].play()
            else:
                self.settle_block()
        else:
            pass
            # self.sounds["block-fall"].play()

    def settle_block(self):
        self.clear_lines()
        with Session.begin_nested():
            self.current_player.blocks += 1
            self.current_player.alltime_blocks += 1
            self.save_to_db()
        self.load_scores()
        self.reserve_block_used = False
        self.move_ended = True
        self.current_block = None
        # self.current_block = self.spawn_block()
        self.remove_input_buttons()

    def remove_input_buttons(self):
        self.home()
        self.objects = [
            HBox(
                [
                    Progress(on_elapsed=self.home, size=70, speed=1 / 5.0),
                ],
                pos=(200, config.SCREEN_HEIGHT),
                align_bottom=True,
                padding=10,
                gap=20,
            )
        ]

    def end_game(self):
        self.sounds["game-over"].play()
        self.current_block = None
        self.game_over = True
        self.reset_game_in_db()
        # self.board = self.load_board()

    def count_full_rows(self) -> int:
        n = 0
        for row in self.board:
            if self.row_is_full(row):
                n += 1
        return n

    def clear_lines(self):
        cleared_lines = 0
        for y, row in enumerate(self.board):
            if self.row_is_full(row):
                self.board.pop(y)
                self.board.insert(0, [Cell() for _ in range(self.BOARD_WIDTH)])
                self.board[0][-1] = Cell(CellType.WALL)
                self.board[0][0] = Cell(CellType.WALL)
                cleared_lines += 1
        self.add_score(cleared_lines)

    def add_score(self, lines: int):
        if lines == 0:
            return
        if lines == 1:
            base_points = 40
        elif lines == 2:
            base_points = 100
        elif lines == 3:
            base_points = 300
        elif lines == 4:
            base_points = 1200
        else:
            assert False, "How did you clear more than 4 lines?"

        points = base_points * (self.level + 1)
        self.score += points
        self.lines += lines
        self.highscore = max(self.highscore, self.score)

        self.current_player.score += points
        self.current_player.lines += lines
        self.current_player.alltime_lines += lines

        if (self.level + 1) * 10 < self.lines and self.level < 20:
            self.level += 1

    @staticmethod
    def row_is_full(row: list[Cell]) -> bool:
        return all(cell.type != CellType.EMPTY for cell in row) and not all(
            cell.type == CellType.WALL for cell in row
        )

    def save_to_db(self):
        with Session.begin_nested():
            game = TetrisGame.query.first()
            game.score = self.score
            game.highscore = self.highscore
            game.level = self.level
            game.lines = self.lines
            game.board = json.loads(json.dumps(self.board, cls=TetrisJSONEncoder))
            game.next_blocks = [b.value for b in self.next_blocks]
            game.reserve_block = self.reserve_block_type

            player = TetrisPlayer.query.filter_by(account_id=self.account.id).first()
            player.score = self.current_player.score
            player.blocks = self.current_player.blocks
            player.lines = self.current_player.lines
            player.alltime_lines = self.current_player.alltime_lines
            player.alltime_blocks = self.current_player.alltime_blocks
            player.alltime_score = self.current_player.alltime_score

            Session.commit()

    def reset_game_in_db(self):
        with Session.begin_nested():
            TetrisGame.query.update(
                {
                    TetrisGame.score: 0,
                    TetrisGame.level: 0,
                    TetrisGame.lines: 0,
                    TetrisGame.next_blocks: [],
                    TetrisGame.board: json.loads(
                        json.dumps(self.generate_empty_board(), cls=TetrisJSONEncoder)
                    ),
                    TetrisGame.reserve_block: random.choice(list(BlockType)),
                }
            )
            TetrisPlayer.query.update(
                {
                    TetrisPlayer.score: 0,
                    TetrisPlayer.blocks: 0,
                    TetrisPlayer.lines: 0,
                }
            )
            Session.commit()

    def render(self, dt):
        self.t += dt
        self.tick()
        surface, debug_surface = super().render(dt)

        def blit(x: int, y: int, sprite_name: str, account_id: int):
            v = Vector2(x, y)
            surface.blit(
                self.sprites[sprite_name],
                v.elementwise() * self.SPRITE_RESOLUTION * self.SCALE,
            )
            if self.current_player.account_id == account_id:
                color = self.current_player.color
            else:
                color = Color.PRIMARY.value
            color_square = pygame.Surface(
                self.SPRITE_RESOLUTION.elementwise() * self.SCALE,
            )
            color_square.fill(color)
            surface.blit(
                color_square,
                v.elementwise() * self.SPRITE_RESOLUTION * self.SCALE,
                special_flags=pygame.BLEND_MULT,
            )
            # pygame.draw.rect(
            #     surface,
            #     (255, 255, 255, 50),
            #     (
            #         v.elementwise() * self.SPRITE_RESOLUTION * self.SCALE,
            #         self.SPRITE_RESOLUTION * self.SCALE,
            #     ),
            # )

        for y in range(self.BOARD_HEIGHT):
            row_is_full = self.row_is_full(self.board[y])
            for x in range(self.BOARD_WIDTH):
                blit(x, y, self.board[y][x].type.sprite, self.board[y][x].account_id)
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
            current_block_surface = self.current_block.render(self.sprites)
            shadow_surface = current_block_surface.copy()
            shadow_surface.fill((0, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
            shadow_pos = self.current_block.shadow_pos
            surface.blit(
                shadow_surface,
                shadow_pos.elementwise() * self.SPRITE_RESOLUTION * self.SCALE,
            )

            surface.blit(
                current_block_surface,
                self.current_block.pos.elementwise()
                * self.SPRITE_RESOLUTION
                * self.SCALE,
            )

        if self.game_over:
            w = 200
            h = 100
            x = (self.BOARD_WIDTH * self.SPRITE_RESOLUTION.x * self.SCALE) // 2 - w // 2
            y = (
                self.BOARD_HEIGHT * self.SPRITE_RESOLUTION.y * self.SCALE
            ) // 2 - h // 2

            pygame.draw.rect(
                surface,
                darken(Color.PRIMARY, 0.8),
                (x, y, w, h),
                border_radius=10,
            )

            font = pygame.font.Font(config.Font.MONOSPACE.value, 20)
            text_surface = font.render("GAME OVER", 1, Color.PRIMARY.value)
            surface.blit(
                text_surface,
                (
                    x + (w - text_surface.get_width()) // 2,
                    y + (h - text_surface.get_height()) // 2,
                ),
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
            self.render_scoreboard(size.x * 0.9, "GAME", self.scores),
            size.elementwise() * Vector2(0.05, 0.42),
        )
        surface.blit(
            self.render_scoreboard(size.x * 0.9, "ALLTIME", self.all_time_scores),
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
        reserve_surface = reserve_shape.render(self.sprites, Color.PRIMARY.value)
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

        font = pygame.font.Font(config.Font.MONOSPACE.value, 20)
        title_level_surface = font.render("LEVEL", 1, Color.BLACK.value)
        title_lines_surface = font.render("LINES", 1, Color.BLACK.value)
        score_surface = font.render(f"SCORE {self.score:8}", 1, Color.BLACK.value)
        highscore_surface = font.render(
            f"HIGHS. {self.highscore:7}", 1, Color.BLACK.value
        )

        level_surface = font.render(f"{self.level:5}", 1, Color.BLACK.value)
        lines_surface = font.render(str(self.lines), 1, Color.BLACK.value)

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

        title_font = pygame.font.Font(config.Font.MONOSPACE.value, 20)
        text_surface = title_font.render(title, 1, Color.BLACK.value)

        label_font = pygame.font.Font(config.Font.MONOSPACE.value, 11)
        lines_label = label_font.render("lines", 1, Color.BLACK.value)
        blocks_label = label_font.render("blocks", 1, Color.BLACK.value)

        lines_label = pygame.transform.rotate(lines_label, -45)
        blocks_label = pygame.transform.rotate(blocks_label, -45)
        surface.blit(lines_label, (size.x - 40, 3))
        surface.blit(blocks_label, (size.x - 80, 3))

        surface.blit(text_surface, (5, 10))
        row_font = pygame.font.Font(config.Font.MONOSPACE.value, 13)

        # only render the scores around the current player, so that they are always visible
        current_player_index = 0
        for i, row in enumerate(scores):
            account, lines, blocks = row
            if account.id == self.current_player.account_id:
                current_player_index = i
                break
        scores = scores[max(0, current_player_index - 4) : current_player_index + 10]

        for i, row in enumerate(scores):
            account, lines, blocks = row
            if account.id == self.current_player.account_id:
                text_color = Color.PRIMARY.value
                pygame.draw.rect(
                    surface,
                    darken(self.current_player.color, 0.6),
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

            pos = i + 1 + max(0, current_player_index - 4)
            text_surface = row_font.render(
                f"{pos:2}. {name:6} {blocks:4} {lines:4}", 1, text_color
            )
            surface.blit(text_surface, (5, 40 + i * 20))
        return surface

    def on_left(self):
        if self.game_over or self.move_ended or not self.current_block:
            return
        self.current_block.move(Direction.LEFT)
        self.sounds["move-block"].play()

    def on_down(self):
        if self.game_over or self.move_ended or not self.current_block:
            return
        play_sound = False
        while self.current_block.fall():
            self.last_tick = self.t
            play_sound = True
        if play_sound:
            self.sounds["block-to-bottom"].play()

    def on_rotate(self, clockwise: bool):
        if self.game_over or self.move_ended or not self.current_block:
            return
        if self.current_block.rotate(clockwise=clockwise):
            self.sounds["rotate-block"].play()

    def on_right(self):
        if self.game_over or self.move_ended or not self.current_block:
            return
        self.current_block.move(Direction.RIGHT)
        self.sounds["move-block"].play()

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
            self.on_rotate(clockwise=True)
        elif event.key == pygame.K_DOWN:
            self.on_rotate(clockwise=False)
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

        return {
            x: pygame.transform.scale(
                pygame.image.load(
                    f"drinks_touch/resources/images/tetris/{x}.png"
                ).convert_alpha(),
                self.SPRITE_RESOLUTION * self.SCALE,
            )
            for x in sprite_names
        }
