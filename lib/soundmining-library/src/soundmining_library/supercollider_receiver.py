import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, cast

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer

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

    @abstractmethod
    def handle_note(self, patch_arguments: PatchArguments) -> None:
        pass

    def current_start_time(self) -> float:
        # Calculate the precise time relative to the music's 'Zero Hour'
        # We use the monotonic delta to avoid jitter from the UDP thread
        elapsed_since_start = time.monotonic() - self.client.mono_start
        return elapsed_since_start - ExtendedNoteHandler.MIDI_DELAY_TIME

    def handle_note_on(self, midi_note: int, velocity: int, device: str) -> None:
        patch_arguments = PatchArguments(
            start=self.current_start_time(),
            midi_note=midi_note,
            velocity=velocity,
            device=device,
            note=midi_note % 12,
            pitch=note.midi_to_hertz(midi_note),
            amp=velocity / 127.0,
            octave=int((midi_note / 12) - 1),
        )

        self.handle_note(patch_arguments)


class SuperColliderReceiver:
    def __init__(self, note_handler: NoteHandler = NoteHandler()) -> None:
        self.note_handler = note_handler
        self.transport = None
        self.protocol = None
        self.server = None

    def default_handler(self, address: str, *args: list[Any]) -> None:
        match address:
            case "/noteOn":
                self.note_handler.handle_note_on(cast(int, args[0]), cast(int, args[1]), cast(str, args[2]))
            case "/noteOff":
                self.note_handler.handle_note_off(cast(int, args[0]), cast(int, args[1]), cast(str, args[2]))
            case "/cc":
                self.note_handler.handle_cc(cast(int, args[0]), cast(int, args[1]), cast(str, args[2]))
            case "/bend":
                self.note_handler.handle_bend(cast(int, args[0]), cast(str, args[1]))

    def set_note_handler(self, note_handler: NoteHandler) -> None:
        self.note_handler = note_handler

    async def start(self) -> None:
        logging.info("Start supercollider receiver")
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self.default_handler)
        loop = asyncio.get_event_loop()
        self.server = AsyncIOOSCUDPServer(("127.0.0.1", 57111), dispatcher, loop)
        self.transport, self.protocol = await self.server.create_serve_endpoint()
        logging.info("Async Receiver is live.")

        # self.server = BlockingOSCUDPServer(("127.0.0.1", 57111), dispatcher)
        # self.executor.submit(self.run_supercollider_server)

    def stop(self) -> None:
        logging.info("Stop supercollider receiver")
        if self.transport:
            self.transport.close()
            self.transport = None
