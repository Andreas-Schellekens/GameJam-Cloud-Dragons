import unittest
from src.game import Game

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_initialization(self):
        self.assertIsNotNone(self.game)

    def test_update(self):
        initial_state = self.game.state
        self.game.update()
        self.assertNotEqual(initial_state, self.game.state)

    def test_draw(self):
        # Assuming draw method does not return anything but modifies the game state
        initial_state = self.game.state
        self.game.draw()
        self.assertEqual(initial_state, self.game.state)  # Placeholder for actual draw validation

if __name__ == '__main__':
    unittest.main()