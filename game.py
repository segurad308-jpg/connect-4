from game_objects import *
from team_strategy import *
from random_strategy import *
from mariusnico import *
import time

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
    print(b1)

    plays_to_make = height * width
    tour = 1

    while True:
        for player in [s1, s2]:
            start = time.time()

            p = player.play(b1)


            end = time.time()
            time_f = (end - start)
            print(f"Temps pour trouver un coup: {time_f}")

            print(f"{player.name} : colonne {p + 1}")
            b1.play(p, player._my_color)

            win_or_not = check_winner_global(b1, to_win)
            if win_or_not is not None:
                print(b1)
                print(f"Victoire du joueur {player.name}")
                return

            print(b1)

        else:
            if tour == plays_to_make:
                print("Égalité... Personne ne gagne ce coup ci !")
                break

            tour += 1

if __name__ == "__main__":
    play_game(KeyboardStrategy(Token.YELLOW), TeamStrategy(Token.RED), height=6, width=7)



