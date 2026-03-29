
class BusAllocator:
    def __init__(self, start_channel: int) -> None:
        self.start_channel = start_channel
        self.reset_allocations()

    def __allocate_new_channels(self, nr_of_channels: int) -> tuple[int]:
        if not self.allocations:
            return tuple(range(self.start_channel, self.start_channel + nr_of_channels))
        else:
            max_channel = max(map(lambda x: max(x), self.allocations.keys()))
            return tuple(range(max_channel + 1, max_channel + 1 + nr_of_channels))

    def reset_allocations(self) -> None:
        self.allocations = dict()

    def __add_new_channels_allocation(self, nr_of_channels, start: float, end: float) -> tuple[int]:
        channels = self.__allocate_new_channels(nr_of_channels)
        self.allocations[channels] = [(start, end)]
        return channels

    def __add_channel_allocation(self, channels: tuple[int], start: float, end: float) -> tuple[int]:
        self.allocations[channels].append((start, end))
        return channels

    def allocate(self, nr_of_channels: int, start: float, end: float) -> tuple[int]:
        for channels, allocs in self.allocations.items():
            if len(channels) == nr_of_channels and all(map(lambda x: not does_overlap(start, end, x[0], x[1]), allocs)):
                return self.__add_channel_allocation(channels, start, end)
        return self.__add_new_channels_allocation(nr_of_channels, start, end)


def does_overlap(start: float, end: float, alloc_start: float, alloc_end: float) -> bool:
    return (is_between(start, alloc_start, alloc_end) or
            is_between(end, alloc_start, alloc_end) or
            (start <= alloc_start and end >= alloc_end))


def is_between(value: float, start: float, end: float) -> bool:
    return value >= start and value <= end
