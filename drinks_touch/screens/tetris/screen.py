import functools
import json
import logging
import math
import random
from collections import Counter
from datetime import datetime

import pygame
from pygame import Vector2
from pygame.mixer import Sound
from sqlalchemy import select

import config
from config import Color
from database.models import Account, TetrisPlayer, TetrisGame
from database.storage import Session, with_db
from elements import Button, SvgIcon, Progress
from elements.hbox import HBox
from elements.spacer import Spacer
from screens.screen import Screen
from screens.tetris.block import Block, BlockType, Direction
from screens.tetris.board import Board
from screens.tetris.cell import Cell, CellType
from screens.tetris.constants import (
    BOARD_WIDTH,
    BOARD_HEIGHT,
    SCALE,
    SPRITE_RESOLUTION,
    GAME_START_COUNTDOWN,
)
from screens.tetris.gameinfo import GameInfo
from screens.tetris.player import Player
from screens.tetris.shape import Shape
from screens.tetris.utils import clamp, darken

logger = logging.getLogger(__name__)


@functools.cache
@with_db
def get_name_for_account_id(account_id: int) -> str:
    query = select(Account.name).where(Account.id == account_id)
    name = Session().execute(query).scalar_one()
    return name


class TetrisJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Cell):
            return [o.type, o.account_id]
        return super().default(o)


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Convert an (R, G, B) tuple to a hex string."""
    return "#{:02X}{:02X}{:02X}".format(*rgb)


class TetrisScreen(Screen):
    nav_bar_visible = False
    background_color = darken(Color.PRIMARY, 0.8)

    @classmethod
    @functools.lru_cache(maxsize=16)
    def get_sound(cls, sound_name: str) -> Sound:
        return Sound(f"drinks_touch/resources/sounds/tetris/{sound_name}.wav")

    def __init__(self, account: Account):
        super().__init__()
        today = datetime.now().date()
        self.april_fools = today.month == 4 and today.day == 1

        self.t = 0
        self.last_tick = 0
        self.loading = True
        self.account = account
        self.scores: list[tuple[int, str, int, int]] = []
        self.all_time_scores: list[tuple[int, str, int, int]] = []
        self.score = 0
        self.highscore = 0
        self.lines = 0
        self.removed_pixels = Counter()
        self.scored_points = []
        self.cleared_lines = 0
        self.reserve_block_type = None
        self.reserve_block_used = False
        # self.board: list[list[Cell]] = TetrisScreen.generate_empty_board()
        self.board: list[list[Cell]] = [[]]
        self.level = 0
        self.next_blocks: list[BlockType] = []
        self.current_player: Player | None = None
        self.current_block: Block | None = None
        self.game_over = False
        self.move_ended = False
        self.game_started = False
        self.game_starts_at = None
        self.game_starts_in = 0
        self.hide_full_row = False
        self.gameinfo = GameInfo(self, self.scores, self.all_time_scores)
        self.board_obj = Board(self)

        self.objects = []

    @with_db
    def on_start(self, *args, **kwargs):
        query = select(TetrisGame)
        tetris_game = Session().execute(query).scalar_one_or_none()
        if not tetris_game:
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

        self.reserve_block_type = self.load_reserve_block()
        self.board = self.load_board()
        self.level = self.load_level()
        self.next_blocks: list[BlockType] = self.load_next_blocks()
        self.load_scores()

        if not self.current_player:
            self.load_color_selection_buttons()

        self.loading = False

    def load_control_buttons(self):
        def icon(filename: str):
            return SvgIcon(
                f"drinks_touch/resources/images/{filename}.svg",
                height=50,
                color=Color.PRIMARY,
            )

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

    def load_color_selection_buttons(self):
        def color_button(color: Color):
            return Button(
                text="",
                on_click=functools.partial(self.on_color_selected, color),
                color=Color.BLACK,
                bg_color=color,
                inner=Spacer(width=28, height=40),
            )

        self.objects = [
            HBox(
                [
                    color_button(Color.ORANGE),
                    color_button(Color.RED),
                    color_button(Color.MAGENTA),
                    color_button(Color.PURPLE),
                    color_button(Color.BLUE),
                    color_button(Color.CYAN),
                    color_button(Color.GREEN),
                ],
                pos=(5, config.SCREEN_HEIGHT),
                align_bottom=True,
                padding=(20, 10),
                gap=20,
            )
        ]

    def load_game_over_buttons(self):
        self.objects = [
            Button(
                text="Tschüss",
                on_click=self.home,
                size=30,
                pos=(config.SCREEN_WIDTH // 2 - 70, config.SCREEN_HEIGHT - 20),
                align_bottom=True,
            ),
        ]

    @with_db
    def on_color_selected(self, color: Color):
        if self.current_player:
            # Due to the pi lagging, it can happen that the on_click handler is
            # triggered multiple times. To avoid inserting a player multiple
            # times and therefore getting a unique constraint violation, we
            # check if self.current_player has already been set
            logger.warning("Player already set. Skipping creation.")
            return
        p = TetrisPlayer(
            account_id=self.account.id,
            score=0,
            blocks=0,
            lines=0,
            points=0,
            alltime_score=0,
            alltime_blocks=0,
            alltime_lines=0,
            alltime_points=0,
            color=rgb_to_hex(color.value),
        )
        Session.add(p)
        self.current_player = Player(p)

    def spawn_block(self, block_type: None | BlockType = None) -> Block:
        if not block_type:
            block_type = self.draw_block()
        return Block(
            shape=Shape(block_type),
            pos=Vector2(BOARD_WIDTH // 2 - 1, 0),
            board=self.board,
            player=self.current_player,
        )

    def load_level(self) -> int:
        # game = TetrisGame.query.first()
        # if game.level:
        #     return game.level
        # return 0
        query = select(TetrisGame.level)
        return Session().execute(query).scalar_one_or_none() or 0

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
        return TetrisScreen.generate_empty_board()

    @classmethod
    def generate_empty_board(cls) -> list[list[Cell]]:
        empty = [[Cell() for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        with_walls = [
            [
                (
                    Cell(CellType.WALL)
                    if x in (0, BOARD_WIDTH - 1) or y == BOARD_HEIGHT - 1
                    else c
                )
                for x, c in enumerate(r)
            ]
            for y, r in enumerate(empty)
        ]
        return with_walls

    @staticmethod
    def draw_message_box(surface: pygame.Surface, message: str):
        w = 200
        h = 100

        x = (BOARD_WIDTH * SPRITE_RESOLUTION.x * SCALE) // 2 - w // 2
        y = (BOARD_HEIGHT * SPRITE_RESOLUTION.y * SCALE) // 2 - h // 2

        pygame.draw.rect(
            surface,
            TetrisScreen.background_color,
            (x, y, w, h),
            border_radius=10,
        )

        font = pygame.font.Font(config.Font.MONOSPACE.value, 20)

        line_surfaces = [
            font.render(line, 1, Color.PRIMARY.value) for line in message.splitlines()
        ]

        if len(line_surfaces) == 1:
            text_surface = line_surfaces[0]
        else:
            total_height = sum(line.get_height() for line in line_surfaces)
            largest_width = max(line.get_width() for line in line_surfaces)
            text_surface = pygame.Surface(
                (largest_width, total_height), pygame.SRCALPHA
            )
            y_offset = 0
            for line in line_surfaces:
                x_offset = (largest_width - line.get_width()) // 2
                text_surface.blit(line, (x_offset, y_offset))
                y_offset += line.get_height()

        surface.blit(
            text_surface,
            (
                x + (w - text_surface.get_width()) // 2,
                y + (h - text_surface.get_height()) // 2,
            ),
        )

    def load_reserve_block(self) -> BlockType:
        return TetrisGame.query.first().reserve_block

    @with_db
    def load_scores(self):
        query = Session().query(TetrisPlayer, Account).join(Account)

        scores_query = query.filter(TetrisPlayer.blocks > 0).order_by(
            TetrisPlayer.points.desc(), TetrisPlayer.blocks.desc()
        )
        self.scores = [
            (account.id, account.name, score.blocks, score.points)
            for score, account in scores_query
        ]

        all_time_scores_query = query.filter(TetrisPlayer.alltime_blocks > 0).order_by(
            TetrisPlayer.alltime_points.desc(), TetrisPlayer.alltime_blocks.desc()
        )
        self.all_time_scores = [
            (account.id, account.name, player.alltime_blocks, player.alltime_points)
            for player, account in all_time_scores_query
        ]
        self.gameinfo = GameInfo(self, self.scores, self.all_time_scores)
        game = TetrisGame.query.first()
        self.score = game.score
        self.highscore = game.highscore
        self.level = game.level
        self.lines = game.lines
        if p := TetrisPlayer.query.filter_by(account_id=self.account.id).first():
            self.current_player = Player(p)
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
        self.get_sound("use-reserve").play()

    @with_db
    def tick(self, dt):
        self.t += dt
        super().tick(dt)
        self.gameinfo.tick(dt)
        if self.game_over:
            if self.t - self.last_tick < 1.5:
                return
            self.last_tick = self.t
            # cycle through the highscores by switching the current player
            i = 0
            for i, (account_id, _, _, _) in enumerate(self.scores):
                if account_id == self.account.id:
                    break
            i -= 1
            if i < 0:
                i = len(self.scores) - 1
            query = select(Account).where(Account.id == self.scores[i][0])
            self.account = Session().execute(query).scalar_one()
            query = select(TetrisPlayer).where(
                TetrisPlayer.account_id == self.account.id
            )
            self.current_player = Player(Session().execute(query).scalar_one_or_none())

            return

        if not self.game_started:
            if self.loading:
                return
            if self.game_starts_at is None and self.current_player:
                self.game_starts_at = self.t + GAME_START_COUNTDOWN
                self.current_block = self.spawn_block()
                self.load_control_buttons()
            if self.game_starts_at:
                if self.t >= self.game_starts_at:
                    self.game_started = True
                else:
                    # need to clamp because of floating point errors, self.game_starts_at can be slightly above self.t
                    self.game_starts_in = round(
                        clamp(self.game_starts_at - self.t, 0, GAME_START_COUNTDOWN),
                        2,
                    )
            return

        if self.move_ended:
            return

        if not self.current_block:
            self.hide_full_row = math.sin(self.t * 15) < 0
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
            self.get_sound("lock-block").play()
            if self.current_block.overlapping:
                self.end_game()
                return

            if n := self.count_full_rows():
                self.current_block = None
                if n == 4:
                    self.get_sound("4-line-clear").play()
                else:
                    self.get_sound("line-clear").play()
            else:
                self.settle_block()
        else:
            pass
            # self.sounds["block-fall"].play()

    def settle_block(self):
        self.clear_lines()
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
        # leave screen quickly; debugging purposes
        # if not self.scored_points:
        #     self.home()
        self.objects = [
            HBox(
                [
                    Progress(on_elapsed=self.home, size=70, speed=1000 / 7.5),
                ],
                pos=(200, config.SCREEN_HEIGHT),
                align_bottom=True,
                padding=10,
                gap=20,
            )
        ]

    def end_game(self):
        self.get_sound("game-over").play()
        self.current_block = None
        self.game_over = True
        self.reset_game_in_db()
        self.load_game_over_buttons()
        # self.board = self.load_board()

    def count_full_rows(self) -> int:
        n = 0
        for row in self.board:
            if self.row_is_full(row):
                n += 1
        return n

    def clear_lines(self):
        removed_pixels = Counter()
        cleared_lines = 0
        for y, row in enumerate(self.board):
            if self.row_is_full(row):
                completed_row = self.board.pop(y)
                for cell in completed_row:
                    if cell.account_id == -1:
                        # Skip wall cells
                        continue
                    removed_pixels[cell.account_id] += 1
                self.board.insert(0, [Cell() for _ in range(BOARD_WIDTH)])
                self.board[0][-1] = Cell(CellType.WALL)
                self.board[0][0] = Cell(CellType.WALL)
                cleared_lines += 1
        self.add_score(cleared_lines, removed_pixels)
        return removed_pixels

    def add_score(self, lines: int, removed_pixels: Counter[int]):
        assert sum(removed_pixels.values()) == lines * (BOARD_WIDTH - 2)
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

        self.removed_pixels += removed_pixels
        self.cleared_lines = lines

        if (self.level + 1) * 10 < self.lines and self.level < 20:
            self.level += 1

    @staticmethod
    def row_is_full(row: list[Cell]) -> bool:
        return all(cell and cell.type != CellType.EMPTY for cell in row) and not all(
            cell.type == CellType.WALL for cell in row
        )

    @with_db
    def save_to_db(self):
        game = TetrisGame.query.first()
        game.score = self.score
        game.highscore = self.highscore
        game.level = self.level
        game.lines = self.lines
        game.board = json.loads(json.dumps(self.board, cls=TetrisJSONEncoder))
        game.next_blocks = [b.value for b in self.next_blocks]
        game.reserve_block = self.reserve_block_type

        scored_points = []

        for account_id, pixels in self.removed_pixels.items():
            # player = TetrisPlayer.query.filter_by(account_id=account_id).first()
            if account_id == self.current_player.account_id:
                factor = self.cleared_lines
            else:
                factor = 1
            TetrisPlayer.query.filter_by(account_id=account_id).update(
                {
                    TetrisPlayer.points: TetrisPlayer.points + pixels * factor,
                    TetrisPlayer.alltime_points: TetrisPlayer.alltime_points
                    + pixels * factor,
                }
            )
            scored_points.append((account_id, pixels, pixels * factor))

        TetrisPlayer.query.filter_by(account_id=self.current_player.account_id).update(
            {
                TetrisPlayer.score: self.current_player.score,
                TetrisPlayer.lines: self.current_player.lines,
                TetrisPlayer.alltime_lines: self.current_player.alltime_lines,
                TetrisPlayer.blocks: self.current_player.blocks,
                TetrisPlayer.alltime_blocks: self.current_player.alltime_blocks,
            }
        )

        self.scored_points = sorted(scored_points, key=lambda x: x[2], reverse=True)
        self.removed_pixels.clear()

    @with_db
    def reset_game_in_db(self):
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
                TetrisPlayer.points: 0,
            }
        )

    def calculate_hash(self):
        super_hash = super().calculate_hash()
        return hash(
            (
                super_hash,
                self.loading,
                tuple(self.scores),
                tuple(self.all_time_scores),
                self.score,
                self.highscore,
                self.lines,
                tuple(self.scored_points),
                self.reserve_block_type,
                self.reserve_block_used,
                self.level,
                tuple(self.next_blocks),
                self.game_over,
                self.move_ended,
                self.game_started,
                self.game_starts_at,
                self.game_starts_in,
                self.gameinfo.calculate_hash(),
                self.board_obj.calculate_hash(),
            )
        )

    def _render(self):
        surface, debug_surface = super()._render()

        board_surface = self.board_obj.render()

        if self.april_fools:
            board_surface = pygame.transform.flip(board_surface, True, True)

        surface.blit(board_surface, (0, 0))

        if self.loading:
            TetrisScreen.draw_message_box(surface, "Lade…")
            pygame.draw.arc(
                surface,
                Color.PRIMARY.value,
                ((self.width - 70) / 2, self.height - 85, 70, 70),
                math.pi - self.t * 5,
                math.pi * 1.4 - self.t * 5,
                width=int(70 / 5),
            )

        if self.game_over:
            TetrisScreen.draw_message_box(surface, "GAME OVER")

        if not self.loading and not self.game_started and not self.current_player:
            TetrisScreen.draw_message_box(surface, "Wähle deine\nFarbe")

        if not self.game_started and self.game_starts_at:
            w = 200
            h = 200
            x = (BOARD_WIDTH * SPRITE_RESOLUTION.x * SCALE) // 2 - w // 2
            y = (BOARD_HEIGHT * SPRITE_RESOLUTION.y * SCALE) // 2 - h // 2

            pygame.draw.rect(
                surface,
                TetrisScreen.background_color,
                (x, y, w, h),
                border_radius=10,
            )
            small_font = pygame.font.Font(config.Font.MONOSPACE.value, 20)
            big_font = pygame.font.Font(config.Font.MONOSPACE.value, 90)

            text_surface_title = small_font.render("LEVEL", 1, Color.PRIMARY.value)
            text_surface_line2 = big_font.render(
                str(self.level), 1, Color.PRIMARY.value
            )
            surface.blit(
                text_surface_line2,
                (
                    x + (w - text_surface_line2.get_width()) // 2,
                    y + (h - text_surface_line2.get_height()) // 2,
                ),
            )
            surface.blit(
                text_surface_title,
                (
                    x + (w - text_surface_title.get_width()) // 2,
                    y + 10,
                ),
            )

            progress_bar_from = Vector2(x, y + h - 20)
            progress_bar_to = Vector2(x + w, y + h - 20)

            rect_w = (
                progress_bar_to.lerp(
                    progress_bar_from,
                    1 - self.game_starts_in / GAME_START_COUNTDOWN,
                ).x
                - progress_bar_from.x
            )
            rect = (
                progress_bar_from.x,
                progress_bar_from.y,
                rect_w,
                20,
            )
            pygame.draw.rect(
                surface,
                Color.PRIMARY.value,
                rect,
                border_radius=10,
            )

        if self.move_ended and self.scored_points:
            w = 200
            h = 30 * len(self.scored_points) + 10
            x = SPRITE_RESOLUTION.x * SCALE + 4
            y = (BOARD_HEIGHT * SPRITE_RESOLUTION.y * SCALE) // 2 - h // 2

            pygame.draw.rect(
                surface,
                TetrisScreen.background_color,
                (x, y, w, h),
                border_radius=10,
            )

            pygame.draw.rect(
                surface,
                Color.PRIMARY.value,
                (x, y, w, h),
                border_radius=10,
                width=3,
            )

            font = pygame.font.Font(config.Font.MONOSPACE.value, 16)
            for i, (account_id, pixels, points) in enumerate(self.scored_points):
                name = get_name_for_account_id(account_id)
                if len(name) > 14:
                    name = name[:13] + "…"
                received_points = f"+{pixels}"
                if self.current_player.account_id == account_id:
                    pygame.draw.rect(
                        surface,
                        darken(self.current_player.color, 0.6),
                        (x + 3, y + i * 30 + 3, w - 6, 34),
                        border_radius=10,
                    )
                text_surface = font.render(
                    f"{name :14} {received_points:>3}",
                    1,
                    Color.PRIMARY.value,
                )
                surface.blit(
                    text_surface,
                    (
                        x + 10,
                        y + i * 30 + 10,
                    ),
                )
                if self.current_player.account_id == account_id:
                    factor = self.cleared_lines
                    badge_x = x + w + 5
                    badge_y = y + i * 30 + 5
                    text_surface = font.render(
                        f"×{factor}",
                        1,
                        Color.PRIMARY.value,
                    )
                    badge_w = text_surface.get_height() + 10
                    badge_h = text_surface.get_width() + 10
                    pygame.draw.rect(
                        surface,
                        darken(self.current_player.color, 0.6),
                        (badge_x, badge_y, badge_w, badge_h),
                    )
                    pygame.draw.rect(
                        surface,
                        Color.PRIMARY.value,
                        (badge_x - 3, badge_y - 3, badge_w + 6, badge_h + 6),
                        border_radius=5,
                        width=3,
                    )
                    surface.blit(text_surface, (badge_x + 5, badge_y + 5))

        scoreboard = self.gameinfo.render()
        surface.blit(scoreboard, (config.SCREEN_WIDTH - scoreboard.get_width(), 0))

        return surface, debug_surface

    def on_left(self):
        if self.loading or self.game_over or self.move_ended or not self.current_block:
            return
        self.current_block.move(Direction.LEFT)
        self.get_sound("move-block").play()

    def on_down(self):
        if self.loading or self.game_over or self.move_ended or not self.current_block:
            return
        play_sound = False
        while self.current_block.fall():
            self.last_tick = self.t
            play_sound = True
        if play_sound:
            self.get_sound("block-to-bottom").play()

    def on_rotate(self, clockwise: bool):
        if self.loading or self.game_over or self.move_ended or not self.current_block:
            return
        if self.current_block.rotate(clockwise=clockwise):
            self.get_sound("rotate-block").play()

    def on_right(self):
        if self.loading or self.game_over or self.move_ended or not self.current_block:
            return
        self.current_block.move(Direction.RIGHT)
        self.get_sound("move-block").play()

    def event(self, event):

        # check if reserve block was clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            x = BOARD_WIDTH * SPRITE_RESOLUTION.x * SCALE + 10
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
        elif event.key == pygame.K_x:
            # for debugging purposes
            self.game_over = True
        else:
            return super().event(event)
        return True
