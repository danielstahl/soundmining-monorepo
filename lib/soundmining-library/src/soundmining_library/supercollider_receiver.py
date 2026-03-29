
import concurrent.futures
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

from soundmining_library import note
from soundmining_library.supercollider_client import SupercolliderClient


class NoteHandler:

    def handle_note_on(self, note: int, velocity: int, device: str) -> None:
        pass

    def handle_note_off(self, note: int, velocity: int, device: str) -> None:
        pass

    def handle_cc(self, value: int, control: int, device: str) -> None:
        pass

    def handle_bend(self, value: int, device: str) -> None:
        pass


@dataclass
class PatchArguments:
    start: float
    midi_note: int
    velocity: int
    device: str
    note: int
    pitch: float
    amp: float
    octave: int


class ExtendedNoteHandler(NoteHandler, ABC):
    MIDI_DELAY_TIME: float = 1.9

    def __init__(self, client: SupercolliderClient) -> None:
        self.client = client

    def current_start_time(self) -> float:
        client = self.client
        if client.clock_time <= 0.0:
            client.reset_clock

        return time.time() - (client.clock_time + ExtendedNoteHandler.MIDI_DELAY_TIME)

    def handle_note_on(self, midi_note: int, velocity: int, device: str) -> None:
        patch_arguments = PatchArguments(
            start=self.current_start_time(),
            midi_note=midi_note,
            velocity=velocity,
            device=device,
            note=midi_note % 12,
            pitch=note.midi_to_hertz(midi_note),
            amp=velocity / 127.0,
            octave=int((midi_note / 12) - 1))

        self.handle_note(patch_arguments)

    @abstractmethod
    def handle_note(patch_arguments: PatchArguments) -> None:
        pass


class SuperColliderReceiver:
    def __init__(self, note_handler: NoteHandler = NoteHandler()) -> None:
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.note_handler = note_handler

    def default_handler(self, address: str, *args: list[any]) -> None:
        match address:
            case "/noteOn":
                self.note_handler.handle_note_on(args[0], args[1], args[2])
            case "/noteOff":
                self.note_handler.handle_note_off(args[0], args[1], args[2])
            case "/cc":
                self.note_handler.handle_cc(args[0], args[1], args[2])
            case "/bend":
                self.note_handler.handle_bend(args[0], args[1])

    def set_note_handler(self, note_handler: NoteHandler) -> None:
        self.note_handler = note_handler

    def run_supercollider_server(self) -> None:
        self.server.serve_forever()

    def start(self) -> None:
        logging.info("Start supercollider receiver")
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self.default_handler)
        self.server = BlockingOSCUDPServer(("127.0.0.1", 57111), dispatcher)
        self.executor.submit(self.run_supercollider_server)

    def stop(self) -> None:
        logging.info("Stop supercollider receiver")
        self.server.shutdown()
        self.server.server_close()
