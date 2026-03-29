import unittest
from soundmining_library.modular.instrument import Bus, AddAction
from soundmining_library.modular.control_instruments import ControlInstruments
from soundmining_library.modular.audio_instruments import AudioInstruments
from soundmining_library import bus_allocator


control_bus_allocator = bus_allocator.BusAllocator(0)
audio_bus_allocator = bus_allocator.BusAllocator(64)


class TestInstrument(unittest.TestCase):

    def test_dynamic_bus(self) -> None:
        allocator = bus_allocator.BusAllocator(64)
        bus = Bus(allocator, 2)
        allocated_bus = bus.dynamic_bus(0, 1)
        self.assertEqual(allocated_bus, 64)

    def test_static_bus(self) -> None:
        allocator = bus_allocator.BusAllocator(64)
        bus = Bus(allocator, 2)
        bus.static_bus(0)
        allocated_bus = bus.dynamic_bus(0, 1)
        self.assertEqual(allocated_bus, 0)

    def test_single_instrument(self) -> None:
        control_instruments = ControlInstruments(control_bus_allocator)
        control_bus_allocator.reset_allocations()
        audio_bus_allocator.reset_allocations()
        result = control_instruments.static_control(5) \
            .build_graph(0, 2)
        expected = [
            ["staticControl", -1, 0, 1004, "out", 0, "dur", 2, "value", 5]
        ]
        self.assertEqual(result, expected)

    def test_block_control(self) -> None:
        control_instruments = ControlInstruments(control_bus_allocator)
        control_bus_allocator.reset_allocations()
        result = control_instruments.two_block_control((0, 1, 0), (1, 1), (0, 0)) \
            .build_graph(0, 3)
        expected = [
            ["twoBlockControl", -1, 0, 1004, "out", 0, "dur", 3, "levels", [0, 1, 0], "times", [1, 1], "curves", [0, 0]]
        ]
        self.assertEqual(result, expected)

    def test_audio_with_control(self) -> None:
        control_instruments = ControlInstruments(control_bus_allocator)

        control_bus_allocator.reset_allocations()
        audio_bus_allocator.reset_allocations()
        freq = control_instruments.static_control(440.0)
        amp = control_instruments.static_control(1.0)
        audio_instruments = AudioInstruments(audio_bus_allocator)
        sine = audio_instruments.sine_osc(amp, freq) \
            .add_action(AddAction.TAIL_ACTION) \
            .static_output_bus(0)

        result = sine.build_graph(0, 2)
        expected = [
            ["staticControl", -1, 0, 1004, "out", 0, "dur", 2, "value", 1.0],
            ["staticControl", -1, 0, 1004, "out", 1, "dur", 2, "value", 440.0],
            ["sineOsc", -1, 1, 1004, "out", 0, "dur", 2, "freqBus", 1, "ampBus", 0]
        ]
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
