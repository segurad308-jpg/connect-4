from cmath import inf
import time
from typing import List
from game_objects import *
import random

# Votre code ici

"""
1. Minimax + alpha beta (objectif: gagner du temps) : Done
2. Move ordering (cibler les meilleurs coups par defaut. Ex: le centre est mieux) : Done
3. Bonne heuristique (Encore trouver les meilleurs critères) : Done

4. Transposition table (Enregistrer les coups déjà calculés pour avoir plus de temps pour les nouveaux)

5. Avoir un coup prêt pour la fin de la limite de temps mais toujours chercher le meilleur. : Done
"""

"""
Les 4 fonction suivante, random_int(), init_table(), index_piece() et findhash(), servent à générer une table
de hashage Zobrist ainsi que accéder à la valeur en hash Zobrist du Board actuel pour ensuite pouvoir 
l'utiliser comme clé dans la transposition table.
"""
def random_int() -> int:
    return random.getrandbits(64)

def init_table() -> List: # genere la table de valeur
    zobrist_table = [[[random_int() for _ in range(2)] for _ in range(7)] for _ in range(6)] # 2 token, 7 width, 6 height
    return zobrist_table

def index_piece(board: Board, row: int, col: int) -> int:
    return 0 if board.box(row, col) == Token.YELLOW else 1

def findhash(board: Board, zobrist_table: list) -> int: # permet de retrouver le hash du board actuel
    hash_value = 0
    for r in range(board.height):
        for c in range(board.width):
            if board.box(r, c) is not None:
                piece = index_piece(board, r, c)
                hash_value ^= zobrist_table[r][c][piece]
    return hash_value

# regarde le nombre de token que le joueur a aligné sur le dernier coup joué
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

    def __init__(self, color: Token):
        super().__init__(color)
        self.deadline = 0.0
        self.zobrist = init_table()
        self.transposition_table = {}  # {clé zobrist : (score, depth)}

    @property
    def name(self) -> str:
        return f"Diego3370"

    def p2_color(self) -> Token:
        if self._my_color == Token.RED:
            return Token.YELLOW
        else:
            return Token.RED

    """
    Pour les 2 méthodes qui suivent, je décide délibérément de ne pas respecter la contrainte imposée par
    python, c'est-à-dire, que je m'autorise à accéder à un attribut privé sans être dans la classe même.
    Je choisis d'utiliser ce "hack" car il me fait gagner énormément de temps et de performance comparé à
    si j'utilisait la fonction générique copy.deepcopy. De plus il s'agit en réalité pas un hack à proprement parlé mais
    plutôt du name mangling officiel et documenté du langage python.
    Si on compare uniquement la copie du Board.__board avec ma fonction play_sim() ou undo(), on est sur du O(42) vs O(1).
    En sachant que cela concerne uniquement la copie du Board.__board et pas le reste.
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

    # organise les colonnes en fonction de leur importance
    def move_ordering(self, board: Board, p2: Token) -> List[int]:
        blocks = []
        good = []
        rest = []

        for col in self.get_playable_cols(board):
            row = self.get_play_token(board, col)

            # instant win no need to look further
            self.play_sim(board, row, col, self._my_color)
            if check_winner(board, row, col, 4) == self._my_color:
                self.undo(board, row, col)
                return [col]
            self.undo(board, row, col)

            # block opps
            self.play_sim(board, row, col, p2)
            if check_winner(board, row, col, 4) == p2:
                self.undo(board, row, col)
                blocks.append(col)
                continue
            self.undo(board, row, col)

            # center cols
            max_dist = board.width // 2
            dist = abs(col - max_dist)
            if dist <= 1:
                good.append(col)
            else:
                rest.append(col)

        return blocks + good + rest

    @staticmethod
    def get_play_token(board: Board, col: int) -> int:
        column = board.column(col)
        row = column.index(None)
        return row

    # dans une window len de 4 on definit la valeur de cette window (valeurs relatives mais logiques entre elles)
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

    # on evalue par window parce que on gagne dans une fenetre de 4 et non sur tout le plateau
    def evaluate(self, board: Board, p2: Token) -> int:
        score = 0

        for l in board.lines():
            for i in range(board.width-2):
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
        score += center_col_array.count(self._my_color) * 3 # more weight to center cols

        return score

    # fonction principale du projet. Inclu une fonction de alpha beta pruning
    def minimax(self, board: Board, depth: int, is_max_player: bool, p2: Token, alpha: float, beta: float, current_hash: int) -> float:
        if time.time() >= self.deadline: # si plus de temps on fait remonter une TimeoutError
            raise TimeoutError

        cols = self.move_ordering(board, p2)

        if not cols:
            return self.evaluate(board, p2)
        if depth == 0:
            return self.evaluate(board, p2)

        # hash du board
        if current_hash in self.transposition_table:
            if self.transposition_table[current_hash][1] >= depth:
                return self.transposition_table[current_hash][0]

        if is_max_player:
            best_score = -inf
            first_move = True
            for col in cols:
                row = self.get_play_token(board, col) # determine the played row

                self.play_sim(board, row, col, self._my_color) # play the move
                try:
                    winner = check_winner(board, row, col, 4)
                    if winner == self._my_color:
                        self.transposition_table[current_hash] = (10000, depth)
                        return 10000

                    piece = index_piece(board, row, col)  # generer un hash du board actuel
                    new_hash = current_hash ^ self.zobrist[row][col][piece]

                    if first_move:
                        score = self.minimax(board, depth - 1, False, p2, alpha, beta, new_hash) # recurse until it reach the leafs
                        first_move = False
                    else:
                        # on cherche dans une fenetre nulle et si le score est est plus grand que prevu on fait une recherche sur tout
                        # en gros cest le concepte PVC (Principal Variation Search)
                        score = self.minimax(board, depth - 1, False, p2, alpha, alpha+1, new_hash)
                        if alpha < score < beta:
                            score = self.minimax(board, depth - 1, False, p2, alpha, beta, new_hash)
                finally:
                    self.undo(board, row, col) # undo the move

                best_score = max(score, best_score)
                alpha = max(alpha, best_score)
                if alpha >= beta: # pruning
                    break

            self.transposition_table[current_hash] = (best_score, depth)
            return best_score

        else:
            best_score = +inf
            first_move = True
            for col in cols:
                row = self.get_play_token(board, col) # determine the played row

                self.play_sim(board, row, col, p2) # play the move
                try:
                    winner = check_winner(board, row, col, 4)
                    if winner == p2:
                        self.transposition_table[current_hash] = (-10000, depth)
                        return -10000
                    piece = index_piece(board, row, col)  # generer un hash du board actuel
                    new_hash = current_hash ^ self.zobrist[row][col][piece]

                    if first_move:
                        score = self.minimax(board, depth - 1, True, p2, alpha, beta, new_hash) # recurse until it reach the leafs
                        first_move = False
                    else:
                        score = self.minimax(board, depth - 1, False, p2, beta-1, beta, new_hash)
                        if alpha < score < beta:
                            score = self.minimax(board, depth - 1, True, p2, alpha, beta, new_hash)

                finally:
                    self.undo(board, row, col)  # undo the move

                best_score = min(score, best_score)
                beta = min(beta, best_score)
                if alpha >= beta: # pruning
                    break

            self.transposition_table[current_hash] = (best_score, depth)
            return best_score

    # check si gagnant potentiel et appelle minimax en iterative deepning
    def search_depth(self, board: Board, depth: int, current_hash: int) -> int:
        best_score = -inf
        p2 = self.p2_color()
        score = None
        cols = self.move_ordering(board, p2)
        best_move = cols[0] # coup de secours

        for col in cols: # check if i can instant win or block opps win
            row = self.get_play_token(board, col)  # determine the played row
            self.play_sim(board, row, col, self._my_color) # play the move

            try:
                if check_winner(board, row, col, 4) == self._my_color: # je gagne
                    return col
            finally:
                self.undo(board, row, col)

            row = self.get_play_token(board, col)
            self.play_sim(board, row, col, p2)  # play the move

            try:
                if check_winner(board, row, col, 4) == p2: # p2 gagne
                    return col
            finally:
                self.undo(board, row, col)

        timeout = False
        for col in cols: # minimax part
            row = self.get_play_token(board, col)  # determine the played row
            self.play_sim(board, row, col, self._my_color) # play the move

            try:
                # generer un hash du board actuel
                piece = index_piece(board, row, col)
                new_hash = current_hash ^ self.zobrist[row][col][piece]

                score = self.minimax(board, depth, False, p2, -inf, +inf, new_hash)  # do the minimax function
            except TimeoutError: # on catch le timeout error pour pas perdre le coup
                timeout = True
                break
            finally:
                self.undo(board, row, col)  # undo the move

            if score is not None:
                if score > best_score:
                    best_score = score
                    best_move = col

        if timeout:
            raise TimeoutError # faire remonter le TimeoutError pour pouvoir le catch dans find_best_move

        return best_move

    # verifie la deadline et augmente la depth tant qu'il y a du temps
    def find_best_move(self, board: Board):
        self.deadline = time.time() + 0.999
        depth = 1
        best_move = self.get_playable_cols(board)[0] # coup de secours
        # hash du board
        current_hash = findhash(board, self.zobrist)

        while time.time() < self.deadline:
            try:
                move = self.search_depth(board, depth, current_hash)
                if move is not None:
                    best_move = move
                depth += 1
            except TimeoutError:
                pass

        return best_move, depth

    def play(self, board: Board): # int est le num de la colonne
        self.transposition_table = {}
        return self.find_best_move(board)
