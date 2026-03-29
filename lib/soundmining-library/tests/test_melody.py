import unittest
from soundmining_library import melody


class TestMelody(unittest.TestCase):
    def test_transpose(self):
        self.assertEqual(melody.transpose(2, [1, 2, 3]), [3, 4, 5])

    def test_shift(self):
        self.assertEqual(melody.shift(2, [1, 2, 3, 4]), [3, 4, 1, 2])

    def test_interval(self):
        self.assertEqual(melody.makeIntervals([4, 5, 6, 3]), [4, 1, 1, -3])

    def test_inverse(self):
        self.assertEqual(melody.inverse([5, 4, 7]), [5, 6, 3])

    def test_reverse(self):
        self.assertEqual(melody.retrograde([1, 2, 3]), [3, 2, 1])

    def test_concrete(self):
        concrete_melody = melody.concrete([0, 1, 0], [1.0, 2.0])
        self.assertEqual(concrete_melody, [1.0, 2.0, 1.0])

    def test_absolut(self):
        relative = [5.0, 4.0]
        self.assertEqual(melody.absolute(0, relative), [0.0, 5.0])

    def test_absolute_with_delta(self):
        relative = [5.0, 4.0]
        self.assertEqual(melody.absolute(5.0, relative), [5.0, 10.0])


if __name__ == '__main__':
    unittest.main()
