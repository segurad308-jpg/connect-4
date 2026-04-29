from game_objects import *
from team_strategy import *
from random_strategy import *
import datetime as dt

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

            win_or_not = check_winner(b1, to_win)
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



