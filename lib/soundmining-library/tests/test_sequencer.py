import unittest
from soundmining_library.sequencer import Sequencer, SequenceNote


class TestSequencer(unittest.TestCase):

    def test_simple_sequence(self) -> None:
        run_result = []

        Sequencer(3) \
            .add_step_handler(lambda i, time: run_result.append((i, time))) \
            .next_time_handler(lambda i: 3) \
            .generate(0)

        expected_result = [(0, 0), (1, 3), (2, 6)]
        self.assertEqual(run_result, expected_result)

    def test_spawn_sequence(self) -> None:
        main_run_result = []
        spawn_run_result = []

        spawn_sequence = Sequencer(2) \
            .add_step_handler(lambda i, time: spawn_run_result.append((i, time))) \
            .start_time_handler(lambda time: time + 1) \
            .next_time_handler(lambda i: 2)

        Sequencer(3) \
            .add_step_handler(lambda i, time: main_run_result.append((i, time))) \
            .next_time_handler(lambda i: 3) \
            .spawn_sequencer(1, spawn_sequence) \
            .generate(0)

        expected_main_result = [(0, 0), (1, 3), (2, 6)]
        self.assertEqual(main_run_result, expected_main_result)

        expected_spawn_result = [(0, 4), (1, 6)]
        self.assertEqual(spawn_run_result, expected_spawn_result)

    def test_simple_sequence_notes(self) -> None:

        def step_handler(i: int, time: float) -> list[SequenceNote]:
            return [
                SequenceNote(time, "Track 1", 1, 0),
                SequenceNote(time + 0.25, "Track 1", 1.25, 1),
            ]

        run_result = Sequencer(2) \
            .add_step_handler(step_handler) \
            .next_time_handler(lambda i: 3) \
            .generate(0)

        expected_result = [
            SequenceNote(0, "Track 1", 1, 0),
            SequenceNote(0.25, "Track 1", 1.25, 1),
            SequenceNote(3, "Track 1", 1, 0),
            SequenceNote(3.25, "Track 1", 1.25, 1),
        ]
        self.assertEqual(run_result, expected_result)

    def test_spawn_sequence_notes(self) -> None:

        def spawn_step_handler(i: int, time: float) -> list[SequenceNote]:
            return [
                SequenceNote(time, "Track 2", 2, 3),
                SequenceNote(time + 0.5, "Track 2", 2.25, 4),
            ]

        spawn_sequence = Sequencer(2) \
            .add_step_handler(spawn_step_handler) \
            .start_time_handler(lambda time: time + 1) \
            .next_time_handler(lambda i: 2)

        def main_step_handler(i: int, time: float) -> list[SequenceNote]:
            return [
                SequenceNote(time, "Track 1", 1, 0),
                SequenceNote(time + 0.25, "Track 1", 1.25, 1),
            ]

        run_result = Sequencer(2) \
            .add_step_handler(main_step_handler) \
            .next_time_handler(lambda i: 3) \
            .spawn_sequencer(1, spawn_sequence) \
            .generate(0)

        expected_result = [
            SequenceNote(0, "Track 1", 1, 0),
            SequenceNote(0.25, "Track 1", 1.25, 1),
            SequenceNote(3, "Track 1", 1, 0),
            SequenceNote(3.25, "Track 1", 1.25, 1),
            SequenceNote(4, "Track 2", 2, 3),
            SequenceNote(4.5, "Track 2", 2.25, 4),
            SequenceNote(6, "Track 2", 2, 3),
            SequenceNote(6.5, "Track 2", 2.25, 4),
        ]
        self.assertEqual(run_result, expected_result)
