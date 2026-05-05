from game_objects import *
from team_strategy import *
from random_strategy import *
import datetime as dt

# meilleur print du board pour mieux voir (fait par chatgpt mais va etre supprimé au moment du rendu)
def print_board(b: Board) -> str:
    board = b._Board__board[::-1]  # afficher du bas vers le haut

    # nombre de colonnes
    cols = len(board[0])

    # construction du plateau
    lines = []

    # numéro des colonnes
    header = "   " + " ".join(f"{i+1}" for i in range(cols))
    lines.append(header)

    # séparateur
    lines.append("  " + "---" * cols)

    # grille
    for row in board:
        line = []
        for cell in row:
            if cell is None:
                line.append("·")  # case vide plus propre qu'un espace
            else:
                line.append(cell.token_display)
        lines.append(" | ".join([" "] + line + [" "]))

    # bas du plateau
    lines.append("  " + "---" * cols)

    return "\n".join(lines)



def find_succession(num_tokens: int, tokens: list[Token]) -> Token | None:
    windows = (tokens[i:i + num_tokens] for i in range(0, len(tokens) - num_tokens + 1))
    for win in windows:
        for tok in [Token.RED, Token.YELLOW]:
            if win.count(tok) == num_tokens:
                return tok
    return None

def check_winner_global(board: Board, req_len: int=4) -> Token | None:
    for l in board.lines():
        if find_succession(req_len, l) is not None:
            return find_succession(req_len, l)

    for c in board.columns():
        if find_succession(req_len, c) is not None:
            return find_succession(req_len, c)

    for d in board.diagonals():
        if find_succession(req_len, d) is not None:
            return find_succession(req_len, d)

    return None

# Votre code ici
class KeyboardStrategy(Strategy):

    def __init__(self, my_color: Token) -> None:
        super().__init__(my_color)
        self._my_color = my_color

    @property
    def name(self) -> str:
        return f"Joueur {self._my_color.team_name}"

    def play(self, board: Board) -> int:
        width = board.width
        height = board.height - 1

        while True:
            col = int(input(f"À votre tour, {self.name}. Quelle colonne ?"))
            if 1 <= col <= width:
                if board.line(height)[col-1] is None:
                    break
                else:
                    raise IllegalMove("La colonne sélectionnée n'est pas valide !")
            else:
                print("La colonne sélectionnée n'est pas valide !")

        return col-1


def play_game(s1: Strategy, s2: Strategy, height=6, width=7):
    b1 = Board()
    to_win = b1.to_win
    print(print_board(b1))

    plays_to_make = height * width
    tour = 1

    while True:
        for player in [s2, s1]:
            start = 0
            if player == s2:
                start = dt.datetime.now()

            p = player.play(b1)

            if player == s2:
                end = dt.datetime.now()
                time = (end - start).total_seconds()
                print(f"Temps pour trouver un coup: {time}")

            print(f"{player.name} : colonne {p + 1}")
            b1.play(p, player._my_color)

            win_or_not = check_winner_global(b1, to_win)
            if win_or_not is not None:
                print(print_board(b1))
                print(f"Victoire du joueur {player.name}")
                return

            print(print_board(b1))

        else:
            if tour == plays_to_make:
                print("Égalité... Personne ne gagne ce coup ci !")
                break

            tour += 1

if __name__ == "__main__":
    play_game(KeyboardStrategy(Token.YELLOW), TeamStrategy(Token.RED), height=6, width=7)



