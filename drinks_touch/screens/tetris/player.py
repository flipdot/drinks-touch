from database.models import TetrisPlayer


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Convert a hex string to an (R, G, B) tuple."""
    hex_str = hex_str.lstrip("#")  # Remove '#' if present
    return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))


class Player:

    def __init__(self, player: TetrisPlayer):
        self.score = player.score
        self.blocks = player.blocks
        self.lines = player.lines
        self.alltime_score = player.alltime_score
        self.alltime_blocks = player.alltime_blocks
        self.alltime_lines = player.alltime_lines
        self.account_id = player.account_id
        self.color = hex_to_rgb(player.color)
