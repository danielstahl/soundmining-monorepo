
from typing import Self, Callable
from dataclasses import dataclass


@dataclass
class SequenceNote:
    start: float
    track: str
    duration: float = 1
    note: int = 0
    freq: float = None
    peak: float = 0.5
    color: str = "black"


class Sequencer:
    def __init__(self, size: int) -> None:
        self.size = size
        self._start_time_handler = lambda start: start
        self.step_handlers = []
        self.spawn_sequences = {}

    def start_time_handler(self, handler: Callable[[float], float]) -> Self:
        self._start_time_handler = handler
        return self

    def next_time_handler(self, handler: Callable[[int], float]) -> Self:
        self.next_time_handler = handler
        return self

    def add_step_handler(self, handler: Callable[[int, float], list[SequenceNote]]) -> Self:
        self.step_handlers.append(handler)
        return self

    def spawn_sequencer(self, i: int, sequencer: 'Sequencer') -> Self:
        step_spawn_sequencer: list[Sequencer] = self.spawn_sequences.get(i, [])
        step_spawn_sequencer.append(sequencer)
        self.spawn_sequences[i] = step_spawn_sequencer
        return self

    def generate(self, start_time: float) -> list[SequenceNote]:
        sequence_notes = []
        current_time = self._start_time_handler(start_time)
        for i in range(self.size):
            for step_handler in self.step_handlers:
                step_result = step_handler(i, current_time) or []
                sequence_notes.extend(step_result)
            for spawn_sequencer in self.spawn_sequences.get(i, []):
                spawn_result = spawn_sequencer.generate(current_time) or []
                sequence_notes.extend(spawn_result)
            current_time = max(current_time + self.next_time_handler(i), 0)
        return sequence_notes
