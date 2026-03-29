import unittest

from soundmining_library.ui.ui_piece import UiPieceBuilder, UiPiece, UiTrack
from soundmining_library.sequencer import SequenceNote


class TestUiPiece(unittest.TestCase):

    def test_build_piece(self) -> None:
        ui_builder = UiPieceBuilder()
        ui_builder.add_note(SequenceNote(0, "Track 1", duration=3, note=1, peak=0.5))
        ui_builder.add_note(SequenceNote(1, "Track 1", duration=3, note=2, peak=0.5))
        ui_builder.add_note(SequenceNote(0, "Track 2", duration=5, note=3, peak=0.33))
        piece = ui_builder.build()

        expected_piece = UiPiece([
            UiTrack("Track 1", [
                SequenceNote(start=0, track="Track 1", duration=3, note=1, peak=0.5),
                SequenceNote(start=1, track="Track 1", duration=3, note=2, peak=0.5)
            ]),
            UiTrack("Track 2", [
                SequenceNote(0, "Track 2", duration=5, note=3, peak=0.33)
            ])
            ])

        self.assertEqual(piece, expected_piece)

    def test_add_notes(self) -> None:

        sequence_notes = [
            SequenceNote(0, "Track 1", duration=3, note=1, peak=0.5),
            SequenceNote(1, "Track 1", duration=3, note=2, peak=0.5),
            SequenceNote(0, "Track 2", duration=5, note=3, peak=0.33),
        ]

        piece = UiPieceBuilder() \
            .add_notes(sequence_notes) \
            .build()

        expected_piece = UiPiece([
            UiTrack("Track 1", [
                SequenceNote(0, "Track 1", duration=3, note=1, peak=0.5),
                SequenceNote(1, "Track 1", duration=3, note=2, peak=0.5)
            ]),
            UiTrack("Track 2", [
                SequenceNote(0, "Track 2", duration=5, note=3, peak=0.33),
            ])
            ])

        self.assertEqual(piece, expected_piece)
