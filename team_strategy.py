from cmath import inf
import copy
from typing import *
from game_objects import *

# Votre code ici

"""
1. Minimax + alpha beta (objectif: gagner du temps) : Done
2. Move ordering (cibler les meilleurs coups par defaut. Ex: le centre est mieux)
Trop de poids est donné aux colonnes centrale donc des fois ca ne calcule pas les colonnes loin où je peux gagner

3. Bonne heuristique (Encore trouver les meilleurs critères)
Pour l'instant le centre rapporte un meilleur score car il est important sauf que il faut que l'IA
sache quand s'arreter quand elle peut pas gagner (elle peut pas aligner 4 pions parce que pas la place)

4. Transposition table (Enregistrer les coups déjà calculés pour avoir plus de temps pour les nouveaux)
5. Avoir un coup prêt pour la fin de la limite de temps mais toujours chercher le meilleur.
"""


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

    # barre horizontale
    if check_direction(board, row, col, 0, 1, req_len, token):
        return token

    # barre verticale
    if check_direction(board, row, col, 1, 0, req_len, token):
        return token

    # diagonale 1
    if check_direction(board, row, col, 1,1, req_len, token):
        return token

    # diagonale 2
    if check_direction(board, row, col, 1, -1, req_len, token):
        return token

    return None


class TeamStrategy(Strategy):

    @property
    def name(self) -> str:
        return f"Diego3370"

    def p2_color(self) -> Token:
        if self._my_color == Token.RED:
            return Token.YELLOW
        else:
            return Token.RED

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

    def center_cols(self, board: Board) -> List[int]:
        cols = self.get_playable_cols(board)
        return sorted(cols, key=lambda c: abs(c - board.width // 2))

    def move_ordering(self, board: Board, p2: Token) -> List[int]: # better move ordering but too heavy to be used rn
        cols_weight = {}
        cols = self.get_playable_cols(board)
        for col in cols:
            weight = 0
            row = self.get_play_token(board, col)

            # simulate to see if this col is a winner
            board.play(col, self._my_color)
            winner = check_winner(board, row, col, 4)
            if winner == self._my_color:
                weight = max(inf, weight)
            board._Board__board[row][col] = None

            # simulate to see if I have to block this col
            board.play(col, p2)
            winner = check_winner(board, row, col, 4)
            if winner == p2:
                weight = max(100, weight)
            board._Board__board[row][col] = None

            # 2 in a row for my token
            board.play(col, self._my_color)
            winner = check_winner(board, row, col, 3)
            if winner == self._my_color:
                weight = max(50, weight)
            board._Board__board[row][col] = None

            # 2 in a row for opps token
            board.play(col, p2)
            winner = check_winner(board, row, col, 3)
            if winner == p2:
                weight = max(30, weight)
            board._Board__board[row][col] = None

            # bonus to center cols
            max_dist = board.width // 2
            dist = abs(col - max_dist)
            weight += ((max_dist - dist) * 5)

            cols_weight[col] = weight

        return sorted(cols, key=lambda c: cols_weight[c], reverse=True)

    @staticmethod
    def get_play_token(board: Board, col: int) -> int:
        column = board.column(col)
        row = column.index(None)
        return row

    def evaluate_window(self, window: list, p2: Token):
        mc = window.count(self._my_color)
        oc = window.count(p2)
        e = window.count(None)

        if oc == 0:
            if mc == 3 and e == 1:
                return 50
            elif mc == 2 and e == 2:
                return 20
            else:
                return 5
        elif mc == 0:
            if oc == 3 and e == 1:
                return -80
            elif oc == 2 and e == 2:
                return -20
            else:
                return -5

        return 0

    def evaluate(self, board: Board, p2: Token) -> int:
        score = 0

        for l in board.lines():
            for i in range(0, board.width-3):
                window = l[i:i+4]
                score += self.evaluate_window(window, p2)

        for c in board.columns():
            for i in range(0, board.height-3):
                window = c[i:i+4]
                score += self.evaluate_window(window, p2)

        for d in board.diagonals():
            for i in range(0, len(d)-3):
                window = d[i:i+4]
                score += self.evaluate_window(window, p2)

        center_col = board.width//2
        center_col_array = board.column(center_col)
        score += center_col_array.count(self._my_color) * 3 # more weight to center cols

        return score

    def minimax(self, board: Board, depth: int, is_max_player: bool, p2: Token, alpha: float, beta: float) -> int:
        cols = self.center_cols(board)

        if depth >= 6:
            return self.evaluate(board, p2)

        if is_max_player:
            best_score = -inf
            for col in cols:
                row = self.get_play_token(board, col) # determine the played row

                board.play(col, self._my_color) # play the move
                winner = check_winner(board, row, col, 4)
                if winner == self._my_color:
                    board._Board__board[row][col] = None
                    return 1

                score = self.minimax(board, depth + 1, False, p2, alpha, beta) # recurse until it reach the leafs

                board._Board__board[row][col] = None # undo the move

                best_score = max(score, best_score)
                alpha = max(alpha, best_score)
                if alpha >= beta: # pruning
                    break

            return best_score

        else:
            best_score = +inf
            for col in cols:
                row = self.get_play_token(board, col) # determine the played row

                board.play(col, p2) # play the move
                winner = check_winner(board, row, col, 4)
                if winner == p2:
                    board._Board__board[row][col] = None
                    return -1

                score = self.minimax(board, depth + 1, True, p2, alpha, beta) # recurse until it reach the leafs

                board._Board__board[row][col] = None  # undo the move

                best_score = min(score, best_score)
                beta = min(beta, best_score)
                if alpha >= beta: # pruning
                    break

            return best_score


    def find_best_move(self, board: Board) -> int:
        p2 = self.p2_color()
        cols = self.move_ordering(board, p2)
        best_score = -inf
        best_move = None

        for col in cols: # check if i can instant win
            row = self.get_play_token(board, col)  # determine the played row
            board.play(col, self._my_color) # play the move

            if check_winner(board, row, col, 4) == self._my_color:
                board._Board__board[row][col] = None
                return col

            board._Board__board[row][col] = None

        for col in cols: # check if i can block opps winner move
            row = self.get_play_token(board, col)  # determine the played row
            board.play(col, p2)  # play the move

            if check_winner(board, row, col, 4) == p2:
                board._Board__board[row][col] = None
                return col

            board._Board__board[row][col] = None

        for col in cols: # minimax part
            row = self.get_play_token(board, col)  # determine the played row
            board.play(col, self._my_color) # play the move

            score = self.minimax(board, 0, False, p2, -inf, +inf)  # do the minimax function

            board._Board__board[row][col] = None  # undo the move

            if score > best_score:
                best_score = score
                best_move = col

        return best_move


    def play(self, board: Board) -> int: # int est le num de la colonne
        return self.find_best_move(board)
