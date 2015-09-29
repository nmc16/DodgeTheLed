import unittest
from src.game.gamemanager import GameManager, HighScore

class TestGameManager(unittest.TestCase):
    """
       Unit test to test if the high scores are stored correctly
    """

    def test_default_user(self):
        """ Check the default high score user """
        gm = GameManager()
        hs = gm.player
        self.assertEqual("no-one", hs.user)
        self.assertEqual(hs.high_score, 0)

    def test_create_new_user(self):
        gm = GameManager()
        gm.change_user("test")
        hs = gm.player
        self.assertEqual(hs.user, "test")
        self.assertEqual(hs.high_score, 0)

    def score_is_saved(self):
        gm = GameManager()
        hs = gm.player
        hs.high_score = 50
        name = hs.user

        gm.change_user("test")
        hs = gm.player
        self.assertNotEqual(hs.user, name)

        gm.change_user(name)
        hs = gm.player
        self.assertEqual(hs.user, name)
        self.assertEqual(hs.high_score, 50)


if __name__ == "__main__":
    unittest.main()
