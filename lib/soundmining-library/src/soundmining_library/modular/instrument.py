
import uuid
from enum import Enum
from typing import Self
from soundmining_library import bus_allocator
from abc import ABC, abstractmethod
from soundmining_library import supercollider_client


class AddAction(Enum):
    HEAD_ACTION = 0
    TAIL_ACTION = 1
    BEFORE_ACTION = 2
    AFTER_ACTION = 3


class NodeId(Enum):
    SOURCE = 1004
    EFFECT = 1005
    ROOM_EFFECT = 1006


def setup_nodes(client: supercollider_client.SupercolliderClient) -> None:
    client.send_message(supercollider_client.group_head(0, NodeId.SOURCE.value))
    client.send_message(supercollider_client.group_tail(NodeId.SOURCE.value, NodeId.EFFECT.value))
    client.send_message(supercollider_client.group_tail(NodeId.EFFECT.value, NodeId.ROOM_EFFECT.value))


DEFAULT_SYNTH_DIR = "/Users/danielstahl/Documents/Projects/soundmining-modular/src/main/sc/synths"


def load_synth_dir(client: supercollider_client.SupercolliderClient, synth_dir: str = DEFAULT_SYNTH_DIR) -> None:
    client.send_message(supercollider_client.load_dir(synth_dir))


class Bus:
    def __init__(self, bus_allocator: bus_allocator.BusAllocator, nr_of_channels: int) -> None:
        self.bus_allocator = bus_allocator
        self.nr_of_channels = nr_of_channels
        self.bus_value = None

    def dynamic_bus(self, start_time: float, end_time: float) -> int:
        if self.bus_value is None:
            self.bus_value = self.bus_allocator.allocate(self.nr_of_channels, start_time, end_time)[0]
        return self.bus_value

    def static_bus(self, bus_value: int) -> int:
        self.bus_value = bus_value
        return self.bus_value

    def get_bus_value(self) -> int:
        return self.bus_value


class Instrument(ABC):
    def __init__(self, instrument_name: str, nr_of_channels: int,
                 output_bus_allocator: bus_allocator.BusAllocator) -> None:
        self.id = str(uuid.uuid1())
        self.instrument_name = instrument_name
        self.nr_of_channels = nr_of_channels
        self._add_action = AddAction.HEAD_ACTION
        self._node_id = NodeId.SOURCE
        self._optional_dur = None
        self.output_bus = Bus(output_bus_allocator, nr_of_channels)
        self.instrument_is_built = False

    def add_action(self, the_value: AddAction) -> Self:
        self._add_action = the_value
        return self

    def node_id(self, the_value: NodeId) -> Self:
        self._node_id = the_value
        return self

    def optional_dur(self, value: float) -> Self:
        self._optional_dur = value
        return self

    def me_in_instrument_list(self, instrument_list: list['Instrument']) -> bool:
        for instrument in instrument_list:
            if instrument.id == self.id:
                return True
        return False

    def prepend_to_graph(self, parent: list['Instrument']) -> list['Instrument']:
        if not self.me_in_instrument_list(parent):
            return [self] + parent
        else:
            return parent

    def append_to_graph(self, parent: list['Instrument']) -> list['Instrument']:
        if not self.me_in_instrument_list(parent):
            return parent + [self]
        else:
            return parent

    @abstractmethod
    def graph(self, parent: list['Instrument']) -> list['Instrument']:
        pass

    @abstractmethod
    def internal_build(self, start_time: float, duration: float) -> list[any]:
        pass

    def get_final_duration(self, duration: float) -> float:
        if self._optional_dur:
            return self._optional_dur
        else:
            return duration

    def dynamic_output_bus(self, start_time: float, duration: float) -> int:
        return self.output_bus.dynamic_bus(start_time, start_time + self.get_final_duration(duration))

    def static_output_bus(self, value: int) -> Self:
        self.output_bus.static_bus(value)
        return self

    def get_output_bus(self) -> int:
        return self.output_bus.get_bus_value()

    def build(self, start_time: float, duration: float) -> list[any]:
        if not self.instrument_is_built:
            final_duration = self.get_final_duration(duration)

            graph = [
                self.instrument_name, -1, self._add_action.value, self._node_id.value,
                "out", self.dynamic_output_bus(start_time, duration),
                "dur", final_duration
            ] + self.internal_build(start_time, duration)
            self.instrument_is_built = True
            return graph
        else:
            return []

    def build_graph(self, start_time: float, duration: float) -> list[list[any]]:
        result = []
        flat_graph = self.graph([])
        for instrument in flat_graph:
            built_instrument = instrument.build(start_time, duration)
            if built_instrument:
                result.append(built_instrument)
        return result


class ControlInstrument(Instrument):
    def __init__(self, instrument_name: str, output_bus_allocator: bus_allocator.BusAllocator) -> None:
        super().__init__(instrument_name, 1, output_bus_allocator)


class AudioInstrument(Instrument):
    def __init__(self, instrument_name: str, nr_of_channels: int,
                 output_bus_allocator: bus_allocator.BusAllocator) -> None:
        super().__init__(instrument_name, nr_of_channels, output_bus_allocator)
