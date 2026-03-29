import unittest
from soundmining_library.sieve import SimpleSieve


class TestSieve(unittest.TestCase):
    def test_simple_sieve(self) -> None:
        sieve = SimpleSieve(2, 0)
        self.assertTrue(sieve.is_sieve(2))
        self.assertFalse(sieve.is_sieve(5))

    def test_simple_sieve_with_offset(self) -> None:
        sieve = SimpleSieve(2, 1)
        self.assertTrue(sieve.is_sieve(3))
        self.assertFalse(sieve.is_sieve(4))


if __name__ == '__main__':
    unittest.main()
