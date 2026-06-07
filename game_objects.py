from abc import ABC, abstractmethod
from enum import Enum
from typing import Iterable

class Token(Enum):
    RED = "🔴", "Red"
    YELLOW = "🟨", "Yellow"

    def __init__(self, *args):
        self.__token_display = args[0]
        self.__team_name = args[1]

    @property
    def team_name(self):
        return self.__team_name

    @property
    def token_display(self):
        return self.__token_display

class IllegalMove(Exception):
    pass

class Board:
    def __init__(self, height: int = 6, width: int = 7, to_win: int = 4):
        self.__board: list[list[Token | None]] = [[None for _ in range(width)] for _ in range(height)]
        self.__height = height
        self.__width = width
        self.__to_win = to_win

    def __repr__(self) -> str:
        return "\n".join(" ".join((token.token_display if token else " ") for token in line) for line in self.__board[::-1])

    @property
    def height(self) -> int:
        return self.__height

    @property
    def width(self) -> int:
        return self.__width

    @property
    def to_win(self) -> int:
        return self.__to_win

    def box(self, row, col) -> Token | None:
        return self.__board[row][col]

    def line(self, index: int) -> list[Token | None]:
        return list(self.__board[index])

    def column(self, index: int) -> list[Token | None]:
        return [line[index] for line in self.__board]

    def diagonals(self) -> Iterable[list[Token | None]]:
        for diagonal_index in range(self.width + self.height - 1):
            # north-west to south-east starting at south-western corner
            yield [self.__board[line_index][column_index]
                   for line_index, column_index in
                   zip(range(diagonal_index, -1, -1), range(0, diagonal_index + 1))
                   if line_index < self.height and column_index < self.width
                   ]
            # north-east to south-west starting at south-eastern corner
            yield [self.__board[line_index][column_index]
                   for line_index, column_index in
                   zip(range(diagonal_index, -1, -1), range(self.width - 1, self.width - diagonal_index - 2, -1))
                   if line_index < self.height and column_index >= 0
                   ]

    def lines(self) -> Iterable[list[Token | None]]:
        return (self.line(l) for l in range(self.height))

    def columns(self) -> Iterable[list[Token | None]]:
        return (self.column(l) for l in range(self.width))

    def play(self, column_index: int, token: Token):
        column = self.column(column_index)
        try:
            drop_height = column.index(None)
        except ValueError:
            raise IllegalMove("Column is already full")
        self.__board[drop_height][column_index] = token

class Strategy(ABC):
    def __init__(self, color: Token):
        self._my_color = color

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def play(self, board: Board) -> int:
        pass
