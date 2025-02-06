from sqlalchemy import Integer, Column, JSON, ForeignKey

from database.storage import Base


class TetrisGame(Base):
    __tablename__ = "tetris__game"
    id = Column(Integer, primary_key=True)
    score = Column(Integer, nullable=False)
    highscore = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)
    lines = Column(Integer, nullable=False)
    next_blocks = Column(JSON)
    board = Column(JSON)
    reserve_block = Column(Integer, nullable=False)


class TetrisPlayer(Base):
    __tablename__ = "tetris__players"
    account_id = Column(ForeignKey("account.id"), primary_key=True)
    score = Column(Integer, nullable=False)
    blocks = Column(Integer, nullable=False)
    lines = Column(Integer, nullable=False)
    pixels = Column(Integer, nullable=False)
    alltime_score = Column(Integer, nullable=False)
    alltime_blocks = Column(Integer, nullable=False)
    alltime_lines = Column(Integer, nullable=False)
    alltime_pixels = Column(Integer, nullable=False)
