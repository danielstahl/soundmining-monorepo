from soundmining_library import bus_allocator, supercollider_client
from soundmining_library.environment import resolve_project_environment
from soundmining_library.modular import instrument
from soundmining_library.modular.sound_play import BufNumAllocator
from soundmining_library.modular_v2 import instruments_v2, synth_player_v2
from soundmining_library.supercollider_client import SupercolliderClient
from soundmining_library.supercollider_receiver import SuperColliderReceiver


class Piece:
    def start(self, should_send_to_score: bool = False) -> None:
        self.environment = resolve_project_environment()
        self.supercollider_client = SupercolliderClient()
        self.supercollider_client.start()
        self.audio_bus_allocator = bus_allocator.BusAllocator(64)
        self.instruments = instruments_v2.InstrumentsV2(self.audio_bus_allocator)
        self.buf_num_allocator = BufNumAllocator()
        self.synth_player = synth_player_v2.SynthPlayerV2(
            self.supercollider_client, self.instruments, self.buf_num_allocator, should_send_to_score=should_send_to_score
        )
        instrument.setup_nodes(self.supercollider_client)
        instrument.load_synth_dir(self.supercollider_client, synth_dir=self.environment.synth_defs)
        receiver = SuperColliderReceiver()
        receiver.start()
        self.receiver = receiver

    def stop(self) -> None:
        self.supercollider_client.stop()
        self.synth_player.stop()
        self.receiver.stop()

    def reset(self) -> None:
        self.synth_player.client.send_message(supercollider_client.clear_sched())
        self.synth_player.client.send_message(supercollider_client.deep_free(0))
        self.audio_bus_allocator.reset_allocations()
        self.supercollider_client.reset_clock()

    def reset_deep(self) -> None:
        instrument.setup_nodes(self.supercollider_client)
        instrument.load_synth_dir(self.supercollider_client, self.environment.synth_defs)
