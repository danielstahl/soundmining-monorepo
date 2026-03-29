import unittest
from soundmining_library import generative


class TestGenerative(unittest.TestCase):
    def test_random_range(self):
        self.assertTrue(2.0 <= generative.random_range(2, 10) <= 10.0)

    def test_pick_items(self):
        choises = ["One", "Two", "Three"]
        choise = generative.pick_items(choises, 2)
        self.assertTrue(len(choise) == 2)
        for i in choise:
            self.assertIn(i, choises)

    def test_weighted_random(self):
        wr = generative.WeightedRandom([("One", 0.5), ("Two", 0.5)])
        value = wr.choose()
        print(value)
        self.assertIn(value, ["One", "Two"])


if __name__ == '__main__':
    unittest.main()
