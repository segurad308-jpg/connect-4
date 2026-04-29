from cmath import inf
import copy
from game_objects import *

# Votre code ici

"""
1. Minimax + alpha beta (objectif: gagner du temps) : Done
2. Move ordering (cibler les meilleurs coups par defaut. Ex: le centre est mieux)
3. Bonne heuristique (Encore trouver les meilleurs critères)
Pour l'instant le centre rapporte un meilleur score car il est important sauf que il faut que l'IA
sache quand s'arreter quand elle peut pas gagner (elle peut pas aligner 4 pions parce que pas la place)
4. Transposition table (Enregistrer les coups déjà calculés pour avoir plus de temps pour les nouveaux)
5. Avoir un coup prêt pour la fin de la limite de temps mais toujours chercher le meilleur.

- Stocker les empty_cells dans un cache pour ne pas devoir les recalculer a chaque fois et gagner du temps
"""

def find_succession(num_tokens: int, tokens: list[Token | None]) -> Token | None:
    windows = (tokens[i:i + num_tokens] for i in range(0, len(tokens) - num_tokens + 1))
    for win in windows:
        if None in win:
            continue
        for tok in [Token.RED, Token.YELLOW]:
            if win.count(tok) == num_tokens:
                return tok
    return None

def check_winner(board: Board, req_len: int) -> Token | None:
    for l in board.lines():
        res = find_succession(req_len, l)
        if res is not None:
            return res

    for c in board.columns():
        res = find_succession(req_len, c)
        if res is not None:
            return res

    for d in board.diagonals():
        res = find_succession(req_len, d)
        if res is not None:
            return res

    return None

class TeamStrategy(Strategy):

    @property
    def name(self) -> str:
        return f"Diego3370"

    def is_empty_col(self, board: Board, col):
        row = board.height - 1
        return board.box(row, col) is None

    def get_playable_cols(self, board: Board):
        cols = []
        for col in range(board.width):
            if self.is_empty_col(board, col):
                cols.append(col)
        return cols

    def copy_board(self, board: Board):
        return copy.deepcopy(board)

    def center_cols(self, board: Board):
        cols = self.get_playable_cols(board)
        return sorted(cols, key=lambda c: abs(c - board.width//2))

    def evaluate(self, board: Board, my_color: Token):
        score = 0

        center_col = board.width//2
        center_col_array = board.column(center_col)
        score += center_col_array.count(my_color) * 3

        return score


    # x = col, y = row
    def minimax(self, board: Board, depth, max_player, alpha, beta):
        cols = self.center_cols(board)

        if self._my_color == Token.RED:
            p1 = self._my_color
            p2 = Token.YELLOW
        else:
            p1 = self._my_color
            p2 = Token.RED

        winner = check_winner(board, 4)
        if winner == self._my_color:
            return 1
        elif winner is not None:
            return -1
        elif len(cols) == 0:
            return 0

        if depth >= 6:
            return self.evaluate(board, p1)

        if max_player:
            best_score = -inf
            for col in cols:
                sim = self.copy_board(board)
                sim.play(col, p1)

                score = self.minimax(sim, depth + 1, False, alpha, beta)

                best_score = max(score, best_score)
                alpha = max(alpha, best_score)

                if alpha >= beta: # pruning
                    break

            return best_score

        else:
            best_score = +inf
            for col in cols:
                sim_board = copy.deepcopy(board)
                sim_board.play(col, p2)

                score = self.minimax(sim_board, depth + 1, True, alpha, beta)

                best_score = min(score, best_score)
                beta = min(beta, best_score)

                if alpha >= beta:
                    break

            return best_score


    def find_best_move(self, board: Board):
        cols = self.center_cols(board)

        best_score = -inf
        best_move = None
        for col in cols:
            sim = self.copy_board(board)
            sim.play(col, self._my_color)
            score = self.minimax(sim, 0, False, -inf, +inf)
            if score > best_score:
                best_score = score
                best_move = col
        return best_move


    def play(self, board: Board) -> int: # int est le num de la colonne
        return self.find_best_move(board)
