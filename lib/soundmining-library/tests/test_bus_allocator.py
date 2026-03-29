import unittest
from soundmining_library import bus_allocator


class TestBusAllocator(unittest.TestCase):
    def test_allocate_mono_track(self) -> None:
        allocator = bus_allocator.BusAllocator(16)
        allocated_channels = allocator.allocate(1, 0, 2)
        self.assertEqual(allocated_channels, (16,))

    def test_allocate_stereo_track(self) -> None:
        allocator = bus_allocator.BusAllocator(16)
        allocated_channels = allocator.allocate(2, 0, 2)
        self.assertEqual(allocated_channels, (16, 17))

    def test_detect_simple_channel_reuse(self) -> None:
        allocator = bus_allocator.BusAllocator(16)
        allocator.allocate(1, 0, 1.99)
        allocated_channels = allocator.allocate(1, 2, 4)
        self.assertEqual(allocated_channels, (16,))

    def test_detect_simple_channel_collision(self) -> None:
        allocator = bus_allocator.BusAllocator(16)
        allocator.allocate(1, 0, 2.0)
        allocated_channels = allocator.allocate(1, 1.5, 3.5)
        self.assertEqual(allocated_channels, (17,))

    def test_detect_simple_equal_channel_collision(self) -> None:
        allocator = bus_allocator.BusAllocator(0)
        allocator.allocate(1, 0, 1)
        allocated_channels = allocator.allocate(1, 0, 1)
        self.assertEqual(allocated_channels, (1,))

    def test_detect_end_channel_collision(self) -> None:
        allocator = bus_allocator.BusAllocator(0)
        allocator.allocate(1, 5.8865767, 6.540641)
        allocated_channels = allocator.allocate(1, 5.886576, 6.671453)
        self.assertEqual(allocated_channels, (1,))

    def test_avoid_exact_match(self) -> None:
        allocator = bus_allocator.BusAllocator(0)
        allocator.allocate(1, 11.119088, 15.370504)
        allocated_channels = allocator.allocate(1, 15.370504, 15.4)
        self.assertEqual(allocated_channels, (1,))
