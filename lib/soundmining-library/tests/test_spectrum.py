import unittest
from soundmining_library import spectrum


class TestSpectrum(unittest.TestCase):
    def test_spectrum(self):
        spect = spectrum.make_spectrum(440.0, 1.0, 4)
        self.assertEqual(spect, [440.0, 880.0, 1320.0, 1760.0])

    def test_undertone_spectrum(self):
        spect = spectrum.make_undertone_spectrum(440.0, 1.0, 4)
        self.assertEqual(spect, [440.0, 220.0, 146.66666666666666, 110.0])

    def test_make_fact(self):
        self.assertEqual(spectrum.make_fact(440.0, 880.0), 1.0)

    def test_fm_synthsis(self):
        fm_synthesis = spectrum.make_fm_synthesis(400, 50, 5)
        expected = list([
            (400.0, 400.0),
            (450.0, 350.0),
            (500.0, 300.0),
            (550.0, 250.0),
            (600.0, 200.0)])
        self.assertEqual(fm_synthesis, expected)

    def test_reflected_fm_synthsis(self):
        fm_synthesis = spectrum.make_fm_synthesis(200, 400, 5)
        expected = list([
            (200.0, 200.0),
            (600.0, 200.0),
            (1000.0, 600.0),
            (1400.0, 1000.0),
            (1800.0, 1400.0)])
        self.assertEqual(fm_synthesis, expected)

    def test_ring_modulate(self):
        self.assertEqual(spectrum.ring_modulate(440, 100), (540, 340))


if __name__ == '__main__':
    unittest.main()
