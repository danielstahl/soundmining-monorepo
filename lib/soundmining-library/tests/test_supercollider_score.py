import unittest

from soundmining_library import supercollider_client, supercollider_score


class TestSupercolliderScore(unittest.TestCase):

    def test_empty_score(self) -> None:
        score = supercollider_score.SupercolliderScore()
        score_string = score.make_score_string()
        print(score_string)
        expected = "[\n[0, [\\c_set, 0, 0]]\n]\n"
        self.assertEqual(score_string, expected)

    def test_g_new(self) -> None:
        score = supercollider_score.SupercolliderScore()
        score.add_message(supercollider_client.group_head(0, 1004))
        score_string = score.make_score_string()
        expected = "[\n[0, [\\g_new, 1004, 0, 0]],\n[0, [\\c_set, 0, 0]]\n]\n"
        self.assertEqual(score_string, expected)

    def test_load_dir(self) -> None:
        score = supercollider_score.SupercolliderScore()
        dir = "/Users/danielstahl/Documents/Projects/soundmining-modular/src/main/sc/synths"
        message_string = score.message_to_string(0, supercollider_client.load_dir(dir))
        expected = f"[0, [\\d_loadDir, '{dir}']]"
        self.assertEqual(message_string, expected)

    def test_simple_new_instrument(self) -> None:
        score = supercollider_score.SupercolliderScore()
        new_synth_message = supercollider_client.new_synth("monoVolume", 1, 1004, ["out", 90, "dur", 8.402653573017457, "in", 89, "ampBus", 24])
        message_string = score.message_to_string(18.994464844699948, new_synth_message)
        expected = "[18.994464844699948, [\\s_new, \\monoVolume, -1, 1, 1004, \\out, 90, \\dur, 8.402653694152832, \\in, 89, \\ampBus, 24]]"
        self.assertEqual(message_string, expected)

    def test_new_instrument_with_array(self) -> None:
        # [11.234355838764865, [\s_new, \twoBlockControl, -1, 0, 1004, \out, 27, \dur, 15.351078398119684, \levels, [0.0, 0.07418931824630097, 0.0], \times, [0.39561834608925445, 0.39679712617529117], \curves, [0.0, 0.0]].asOSCArgArray]
        score = supercollider_score.SupercolliderScore()
        new_synth_message = supercollider_client.new_synth("twoBlockControl", 1, 1004, ["out", 27, "dur", 15.351078398119684, "levels", [0.0, 0.07418931824630097, 0.0], "times", [0.39561834608925445, 0.39679712617529117], "curves", [0.0, 0.0]])
        message_string = score.message_to_string(11.234355838764865, new_synth_message)
        expected = "[11.234355838764865, [\\s_new, \\twoBlockControl, -1, 1, 1004, \\out, 27, \\dur, 15.351078033447266, \\levels, [0.0, 0.07418932020664215, 0.0], \\times, [0.39561834931373596, 0.3967971205711365], \\curves, [0.0, 0.0]].asOSCArgArray]"
        self.assertEqual(message_string, expected)
