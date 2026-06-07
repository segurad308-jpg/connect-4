from cmath import inf
import time
from typing import List
from game_objects import *
import random


"""
The following 4 functions, random_int(), init_table(), index_piece(), and findhash(),
are used to generate a Zobrist hashing table and retrieve the Zobrist hash value
of the current board so it can be used as a key in the transposition table.
"""
def random_int() -> int:
    return random.getrandbits(64)

def init_table() -> List: # generates the value table
    zobrist_table = [[[random_int() for _ in range(2)] for _ in range(7)] for _ in range(6)] # 2 token, 7 width, 6 height
    return zobrist_table

def index_piece(board: Board, row: int, col: int) -> int:
    return 0 if board.box(row, col) == Token.YELLOW else 1

def findhash(board: Board, zobrist_table: list) -> int: # retrieves the hash of the current board
    hash_value = 0
    for r in range(board.height):
        for c in range(board.width):
            if board.box(r, c) is not None:
                piece = index_piece(board, r, c)
                hash_value ^= zobrist_table[r][c][piece]
    return hash_value

# checks how many tokens the player has aligned from the last move played
def check_direction(board: Board, row: int, col: int, dr: int, dc: int, req_len: int, token: Token) -> bool:
    count = 1

    r = row + dr
    c = col + dc

    while 0 <= r < board.height and 0 <= c < board.width and board.box(r, c) == token:
        count += 1
        r += dr
        c += dc

    r = row - dr
    c = col - dc

    while 0 <= r < board.height and 0 <= c < board.width and board.box(r, c) == token:
        count += 1
        r -= dr
        c -= dc

    return count >= req_len

def check_winner(board: Board, row: int, col: int, req_len: int) -> Token | None:
    token = board.box(row, col)
    if token is None:
        return None

    # horizontal line
    if check_direction(board, row, col, 0, 1, req_len, token):
        return token

    # vertical line
    if check_direction(board, row, col, 1, 0, req_len, token):
        return token

    # diagonal 1
    if check_direction(board, row, col, 1,1, req_len, token):
        return token

    # diagonal 2
    if check_direction(board, row, col, 1, -1, req_len, token):
        return token

    return None


class MinimaxStrategy(Strategy):

    def __init__(self, color: Token):
        super().__init__(color)
        self.deadline = 0.0
        self.zobrist = init_table()
        self.transposition_table = {}  # {(zobrist key, player) : (score, depth)}

    @property
    def name(self) -> str:
        return f"Minimax"

    def p2_color(self) -> Token:
        if self._my_color == Token.RED:
            return Token.YELLOW
        else:
            return Token.RED

    """
    For the next two methods, I deliberately choose not to follow the convention imposed by
    Python, meaning that I allow myself to access a private attribute from outside its class.
    I use this "hack" because it provides a huge performance gain compared to using the generic
    copy.deepcopy function. In reality, this is not really a hack but rather the official and
    documented Python name mangling mechanism.
    If we compare only the copy of Board.__board using play_sim() or undo(), we get O(1)
    instead of O(42). This concerns only the copy of Board.__board and not the rest of the object.
    """
    @staticmethod
    def play_sim(board: Board, row: int, col: int, player: Token):
        board._Board__board[row][col] = player

    @staticmethod
    def undo(board: Board, row: int, col: int):
        board._Board__board[row][col] = None

    @staticmethod
    def is_empty_col(board: Board, col: int) -> bool:
        row = board.height - 1
        return board.box(row, col) is None

    def get_playable_cols(self, board: Board) -> List[int]:
        cols = []
        for col in range(board.width):
            if self.is_empty_col(board, col):
                cols.append(col)
        return cols

    # orders columns according to their importance
    def move_ordering(self, board: Board, p2: Token) -> List[int]:
        blocks = []
        good = []
        rest = []

        for col in self.get_playable_cols(board):
            row = self.get_play_token(board, col)

            # immediate win, no need to search further
            self.play_sim(board, row, col, self._my_color)
            if check_winner(board, row, col, 4) == self._my_color:
                self.undo(board, row, col)
                return [col]
            self.undo(board, row, col)

            # block opponent
            self.play_sim(board, row, col, p2)
            if check_winner(board, row, col, 4) == p2:
                self.undo(board, row, col)
                blocks.append(col)
                continue
            self.undo(board, row, col)

            # center columns
            max_dist = board.width // 2
            dist = abs(col - max_dist)
            if dist <= 1:
                good.append(col)
            else:
                rest.append(col)

        return blocks + sorted(good, key=lambda c: abs(c - board.width // 2)) + rest

    @staticmethod
    def get_play_token(board: Board, col: int) -> int:
        column = board.column(col)
        row = column.index(None)
        return row

    # in a window of length 4, define the value of that window
    # (relative values that remain logically consistent)
    def evaluate_window(self, window: list, p2: Token):
        mc = window.count(self._my_color)
        oc = window.count(p2)
        e = window.count(None)

        if oc == 0:
            if mc == 3 and e == 1:
                return 70
            elif mc == 2 and e == 2:
                return 30
            elif mc == 1:
                return 2
        elif mc == 0:
            if oc == 3 and e == 1:
                return -85
            elif oc == 2 and e == 2:
                return -20
            elif oc == 1:
                return -2

        return 0

    # we evaluate by windows because winning occurs within a window of 4,
    # not across the entire board
    def evaluate(self, board: Board, p2: Token) -> int:
        score: int = 0

        for l in board.lines():
            for i in range(board.width-3):
                window = l[i:i+4]
                score += self.evaluate_window(window, p2)

        for c in board.columns():
            for i in range(board.height-3):
                window = c[i:i+4]
                score += self.evaluate_window(window, p2)

        for d in board.diagonals():
            if len(d) < 4:
                continue
            for i in range(len(d)-3):
                window = d[i:i+4]
                score += self.evaluate_window(window, p2)

        center_col = board.width//2
        center_col_array = board.column(center_col)
        score += center_col_array.count(self._my_color) * 7 # more weight given to center columns

        return score

    # main function of the project. Includes alpha-beta pruning
    def minimax(self, board: Board, depth: int, is_max_player: bool, p2: Token, alpha: float, beta: float, current_hash: int) -> float:
        if time.time() >= self.deadline: # if there is no time left, raise a TimeoutError
            raise TimeoutError

        cols = self.move_ordering(board, p2)

        if not cols:
            return self.evaluate(board, p2)
        if depth == 0:
            return self.evaluate(board, p2)

        # board hash 
        key = (current_hash, is_max_player)
        if key in self.transposition_table:
            score, stored_depth = self.transposition_table[key]
            if stored_depth >= depth:
                return score

        if is_max_player:
            best_score: float = -inf
            first_move = True
            for col in cols:
                row = self.get_play_token(board, col) # determine the played row

                self.play_sim(board, row, col, self._my_color) # play the move
                try:
                    winner = check_winner(board, row, col, 4)
                    if winner == self._my_color:
                        self.transposition_table[key] = (10000, depth)
                        return 10000

                    piece = index_piece(board, row, col)  # generate the hash of the current board
                    new_hash = current_hash ^ self.zobrist[row][col][piece]

                    if first_move:
                        score = self.minimax(board, depth - 1, False, p2, alpha, beta, new_hash) # recurse until leaf nodes
                        first_move = False
                    else:
                        # search with a null window and if the score is higher than expected,
                        # perform a full-window search
                        # this is essentially the PVS (Principal Variation Search) concept
                        score = self.minimax(board, depth - 1, False, p2, alpha, alpha+1, new_hash)
                        if alpha < score < beta:
                            score = self.minimax(board, depth - 1, False, p2, alpha, beta, new_hash)
                finally:
                    self.undo(board, row, col) # undo the played move

                best_score = max(score, best_score)
                alpha = max(alpha, best_score)
                if alpha >= beta: # pruning
                    break

            self.transposition_table[key] = (best_score, depth)
            return best_score

        else:
            best_score: float = +inf
            first_move = True
            for col in cols:
                row = self.get_play_token(board, col) 

                self.play_sim(board, row, col, p2) 
                try:
                    winner = check_winner(board, row, col, 4)
                    if winner == p2:
                        self.transposition_table[key] = (-10000, depth)
                        return -10000
                    piece = index_piece(board, row, col)  
                    new_hash = current_hash ^ self.zobrist[row][col][piece]

                    if first_move:
                        score = self.minimax(board, depth - 1, True, p2, alpha, beta, new_hash) 
                        first_move = False
                    else:
                        score = self.minimax(board, depth - 1, True, p2, beta-1, beta, new_hash)
                        if alpha < score < beta:
                            score = self.minimax(board, depth - 1, True, p2, alpha, beta, new_hash)

                finally:
                    self.undo(board, row, col)  

                best_score = min(score, best_score)
                beta = min(beta, best_score)
                if alpha >= beta: 
                    break

            self.transposition_table[key] = (best_score, depth)
            return best_score

    # check for immediate wins and call minimax through iterative deepening
    def search_depth(self, board: Board, depth: int, current_hash: int) -> int:
        best_score: float = -inf
        p2: Token = self.p2_color()
        score: float = -inf
        cols: List[int] = self.move_ordering(board, p2)
        best_move: int = cols[0] # fallback move

        for col in cols: # check if I can win immediately or block the opponent
            row = self.get_play_token(board, col)
            self.play_sim(board, row, col, self._my_color)

            try:
                if check_winner(board, row, col, 4) == self._my_color: # I win
                    return col
            finally:
                self.undo(board, row, col)

            row = self.get_play_token(board, col)
            self.play_sim(board, row, col, p2)  # jouer le coup

            try:
                if check_winner(board, row, col, 4) == p2: # opponent wins
                    return col
            finally:
                self.undo(board, row, col)

        timeout = False
        for col in cols: # minimax section
            row = self.get_play_token(board, col)
            self.play_sim(board, row, col, self._my_color)

            try:
                # generate the hash of the current board
                piece = index_piece(board, row, col)
                new_hash = current_hash ^ self.zobrist[row][col][piece]

                score = self.minimax(board, depth, False, p2, -inf, +inf, new_hash)  # minimax function

            except TimeoutError: # catch the timeout error to avoid losing the move
                timeout = True
                break
            finally:
                self.undo(board, row, col)

            if score is not None:
                if score > best_score:
                    best_score = score
                    best_move = col

        if timeout:
            raise TimeoutError # propagate the TimeoutError so it can be caught in find_best_move


        return best_move

    # check the deadline and increase the depth while there is still time available
    def find_best_move(self, board: Board) -> int:
        self.deadline = time.time() + 0.999
        depth: int = 1
        best_move: int = self.get_playable_cols(board)[0] # fallback move
        
        current_hash = findhash(board, self.zobrist)

        while time.time() < self.deadline:
            try:
                move = self.search_depth(board, depth, current_hash)
                if move is not None:
                    best_move = move
                depth += 1
            except TimeoutError:
                pass

        return best_move

    def play(self, board: Board) -> int: # int is the column number
        self.transposition_table = {}
        return self.find_best_move(board)
