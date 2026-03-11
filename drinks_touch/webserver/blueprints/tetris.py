from flask import Blueprint, render_template
from sqlalchemy import select

from database.models import TetrisGame, TetrisPlayer, Account
from webserver.shared import db

bp = Blueprint("tetris", __name__)

# Block type integer values (from BlockType enum in block.py)
_J = 2
_L = 3
_S = 4
_T = 5
_Z = 6
_O = 7
_I = 8

# Cell type integer values (from CellType enum in cell.py)
_EMPTY = 0
_WALL = 14
_I_VARIANTS = {8, 9, 10, 11, 12, 13}

# CSS class names for each CellType value
_CELL_CSS = {
    0: "cell-empty",
    2: "cell-filled",
    3: "cell-filled",
    4: "cell-filled",
    5: "cell-filled",
    6: "cell-filled",
    7: "cell-filled",
    8: "cell-filled cell-i-h1",
    9: "cell-filled cell-i-h2",
    10: "cell-filled cell-i-h3",
    11: "cell-filled cell-i-v1",
    12: "cell-filled cell-i-v2",
    13: "cell-filled cell-i-v3",
    14: "cell-wall",
}

# Block preview matrices: True = filled cell, False = empty
# Shapes match the initial orientation from shape.py
BLOCK_PREVIEWS = {
    _J: [
        [True, True, True],
        [False, False, True],
    ],
    _L: [
        [True, True, True],
        [True, False, False],
    ],
    _S: [
        [False, True, True],
        [True, True, False],
    ],
    _T: [
        [True, True, True],
        [False, True, False],
    ],
    _Z: [
        [True, True, False],
        [False, True, True],
    ],
    _O: [
        [True, True],
        [True, True],
    ],
    _I: [
        [True, True, True, True],
    ],
}

# Human-readable block type names
BLOCK_NAMES = {
    _J: "J",
    _L: "L",
    _S: "S",
    _T: "T",
    _Z: "Z",
    _O: "O",
    _I: "I",
}


def _cell_css(cell_type: int) -> str:
    return _CELL_CSS.get(cell_type, "cell-empty")


@bp.route("/")
def index():
    game = db.session.execute(select(TetrisGame)).scalar_one_or_none()

    if not game:
        return render_template(
            "tetris/index.html",
            game=None,
            board=[],
            next_blocks=[],
            reserve_block=None,
            scores=[],
            all_time_scores=[],
        )

    # Build player color map: account_id -> hex color string
    players_with_accounts = db.session.execute(
        select(TetrisPlayer, Account).join(
            Account, TetrisPlayer.account_id == Account.id
        )
    ).all()
    player_colors = {p.account_id: p.color for p, _a in players_with_accounts}

    # Process board into renderable rows of {css_class, color} dicts
    board = []
    if game.board:
        for row in game.board:
            board_row = []
            for cell_type, account_id in row:
                color = player_colors.get(account_id) if account_id != -1 else None
                board_row.append(
                    {
                        "css_class": _cell_css(cell_type),
                        "color": color,
                    }
                )
            board.append(board_row)

    # Next blocks: last entries in the list are played first (popped from end)
    next_block_types = list(reversed(game.next_blocks[-3:])) if game.next_blocks else []
    next_blocks = [
        {"name": BLOCK_NAMES.get(bt, "?"), "matrix": BLOCK_PREVIEWS.get(bt)}
        for bt in next_block_types
        if bt in BLOCK_PREVIEWS
    ]

    # Reserve / hold block
    reserve_block = None
    if game.reserve_block and game.reserve_block in BLOCK_PREVIEWS:
        reserve_block = {
            "name": BLOCK_NAMES.get(game.reserve_block, "?"),
            "matrix": BLOCK_PREVIEWS[game.reserve_block],
        }

    # Current-session scoreboard (players with at least one block placed)
    scores_rows = db.session.execute(
        select(TetrisPlayer, Account)
        .join(Account, TetrisPlayer.account_id == Account.id)
        .where(TetrisPlayer.blocks > 0)
        .order_by(TetrisPlayer.points.desc(), TetrisPlayer.blocks.desc())
    ).all()
    scores = [
        {
            "name": a.name,
            "blocks": p.blocks,
            "lines": p.lines,
            "points": p.points,
            "color": p.color,
        }
        for p, a in scores_rows
    ]

    # All-time scoreboard
    all_time_rows = db.session.execute(
        select(TetrisPlayer, Account)
        .join(Account, TetrisPlayer.account_id == Account.id)
        .where(TetrisPlayer.alltime_blocks > 0)
        .order_by(
            TetrisPlayer.alltime_points.desc(), TetrisPlayer.alltime_blocks.desc()
        )
    ).all()
    all_time_scores = [
        {
            "name": a.name,
            "blocks": p.alltime_blocks,
            "lines": p.alltime_lines,
            "points": p.alltime_points,
            "color": p.color,
        }
        for p, a in all_time_rows
    ]

    return render_template(
        "tetris/index.html",
        game=game,
        board=board,
        next_blocks=next_blocks,
        reserve_block=reserve_block,
        scores=scores,
        all_time_scores=all_time_scores,
    )
