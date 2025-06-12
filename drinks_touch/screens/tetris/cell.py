import enum


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
