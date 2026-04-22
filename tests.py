import unittest
from team_strategy import TeamStrategy
from game_objects import *

class TestStrategy(unittest.TestCase):
    def test_name(self):
        strategy = TeamStrategy(color=Token.RED)
        name = strategy.name
        self.assertIsInstance(name, str)

    def test_play(self):
        strategy = TeamStrategy(color=Token.RED)
        board = Board()

        play = strategy.play(board)
        self.assertIn(play, range(board.width))