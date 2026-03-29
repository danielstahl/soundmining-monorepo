import unittest
from soundmining_library import note


# Here is a list of note names. https://pages.mtu.edu/~suits/notefreqs.html
class TestMelody(unittest.TestCase):
    def test_natural(self):
        self.assertEqual(round(note.note_to_hertz("a4")), 440.00)

    def test_sharp(self):
        self.assertEqual(round(note.note_to_hertz("fiss3")), 185.00)

    def test_flat(self):
        self.assertEqual(round(note.note_to_hertz("dess3")), 139)

    # Here is a list of midi to hertz https://www.inspiredacoustics.com/en/MIDI_note_numbers_and_center_frequencies
    def test_midi_to_hertz(self):
        self.assertEqual(note.midi_to_hertz(57), 220.0)


if __name__ == '__main__':
    unittest.main()
