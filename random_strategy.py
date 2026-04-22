import random

from game_objects import *

class RandomStrategy(Strategy):
    @property
    def name(self) -> str:
        return f"Ordinateur (Aléatoire)"

    def play(self, board: Board) -> int:
        available_col = [i for i, v in enumerate(board.line(board.height - 1)) if v is None]
        return random.choice(available_col)