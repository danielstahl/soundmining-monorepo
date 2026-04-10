from typing import Optional, Self

from pythonosc.osc_message import OscMessage

from soundmining_library import supercollider_client
from soundmining_library.modular.instrument import (
    AddAction,
    AudioInstrument,
    NodeId,
)
from soundmining_library.modular.sound_play import BufNumAllocator, SoundPlay
from soundmining_library.modular_v2.instruments_v2 import InstrumentsV2
from soundmining_library.supercollider_client import SupercolliderClient
from soundmining_library.supercollider_score import SupercolliderScore


class SynthPlayerV2:
    def __init__(
        self,
        client: SupercolliderClient,
        instruments: InstrumentsV2,
        buf_num_allocator: BufNumAllocator,
        should_send_to_score: bool = False,
    ) -> None:
        self.client = client
        self.instruments = instruments
        self.buf_num_allocator = buf_num_allocator
        self.supercollider_score = SupercolliderScore()
        self.should_send_to_score = should_send_to_score
        self.sound_plays = {}

    def note(self, node_id: NodeId = NodeId.SOURCE) -> "SynthNoteV2":
        return SynthNoteV2(self, node_id)

    def add_sound(self, name: str, sound_path: str, start: float, end: float) -> Self:
        self.sound_plays[name] = SoundPlay(sound_path, start, end)
        return self

    def get_sound(self, name) -> SoundPlay:
        return self.sound_plays[name]

    def start(self) -> Self:
        self.buf_num_allocator.reset()
        for sound_play in self.sound_plays.values():
            sound_play.init(self.buf_num_allocator.next(), self.client)
        self.supercollider_score.reset()
        return self

    def stop(self) -> Self:
        for sound_play in self.sound_plays.values():
            sound_play.stop(self.client)
        self.buf_num_allocator.reset()
        self.supercollider_score.reset()
        return self


class AudioStack:
    def __init__(self) -> None:
        self.audio_stack = []
        self.duration = 0.0

    def push(self, instrument: AudioInstrument, duration: float = None) -> None:
        self.audio_stack.append(instrument)
        if duration:
            self.duration = max(self.duration, duration)

    def pop(self) -> AudioInstrument:
        return self.audio_stack.pop()


class SynthNoteV2:
    def __init__(self, synth_player: SynthPlayerV2, node_id: NodeId) -> None:
        self.synth_player = synth_player
        self.audio_stack = AudioStack()
        self.input = None
        self.node_id = node_id

    def mono_input(self) -> Self:
        self.input = self.synth_player.instruments.mono_audio_bus()
        return self.push(self.input)

    def stereo_input(self) -> Self:
        self.input = self.synth_player.instruments.stereo_audio_bus()
        return self.push(self.input)

    def input_from_note(self, synth_note: "SynthNoteV2") -> Self:
        assert synth_note.input is not None
        self.input = synth_note.input
        return self.push(self.input)

    def push(self, instrument: AudioInstrument) -> Self:
        self.audio_stack.push(instrument)
        return self

    def sound_mono(
        self,
        sound: str,
        rate: float,
        amp: AudioInstrument,
        start_override: Optional[float] = None,
        end_override: Optional[float] = None,
    ) -> Self:
        synth_player = self.synth_player
        sound_play = synth_player.get_sound(sound)
        start = start_override or sound_play.start
        end = end_override or sound_play.end
        assert sound_play.buf_num is not None
        buf_num: int = sound_play.buf_num
        mono_play_buffer = (
            synth_player.instruments.mono_play_buffer(buf_num, rate, start, end, amp).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        )
        duration = sound_play.duration(rate)
        self.audio_stack.push(mono_play_buffer, duration)
        return self

    def bank_of_osc(self, freqs: list[float], amps: list[float], phases: list[float]) -> Self:
        bank = self.synth_player.instruments.bank_of_osc(freqs, amps, phases).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        return self.push(bank)

    def bank_of_resonators(self, freqs: list[float], amps: list[float], ring_times: list[float]) -> Self:
        in_bus = self.audio_stack.pop()
        bank = (
            self.synth_player.instruments.bank_of_resonators(in_bus, freqs, amps, ring_times).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        )
        return self.push(bank)

    def mono_grain_buf(
        self,
        sound: str,
        grain_trigger_bus: AudioInstrument,
        grain_duration_bus: AudioInstrument,
        grain_rate_bus: AudioInstrument,
        grain_pos_bus: AudioInstrument,
    ) -> Self:
        synth_player = self.synth_player
        sound_play = synth_player.get_sound(sound)
        assert sound_play.buf_num is not None
        grain = (
            synth_player.instruments
            .mono_grain_buf(
                sound_play.buf_num,
                grain_trigger_bus,
                grain_duration_bus,
                grain_rate_bus,
                grain_pos_bus,
            )
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        return self.push(grain)

    def sine(self, freq: AudioInstrument, amp: AudioInstrument) -> Self:
        osc = self.synth_player.instruments.sine_osc(amp, freq).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        return self.push(osc)

    def triangle(self, freq: AudioInstrument, amp: AudioInstrument) -> Self:
        osc = self.synth_player.instruments.triangle_osc(amp, freq).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        return self.push(osc)

    def saw(self, freq: AudioInstrument, amp: AudioInstrument) -> Self:
        osc = self.synth_player.instruments.saw_osc(amp, freq).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        return self.push(osc)

    def pulse(self, freq: AudioInstrument, width: AudioInstrument, amp: AudioInstrument) -> Self:
        osc = self.synth_player.instruments.pulse_osc(amp, freq, width).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        return self.push(osc)

    def dust(self, freq: AudioInstrument, amp: AudioInstrument) -> Self:
        dust = self.synth_player.instruments.dust_osc(amp, freq).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        return self.push(dust)

    def white_noise(self, amp: AudioInstrument) -> Self:
        noise = self.synth_player.instruments.white_noise_osc(amp).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        return self.push(noise)

    def pink_noise(self, amp: AudioInstrument) -> Self:
        noise = self.synth_player.instruments.pink_noise_osc(amp).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        return self.push(noise)

    def mono_high_pass_filter(self, freq_bus: AudioInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        filter = self.synth_player.instruments.mono_high_pass_filter(in_bus, freq_bus).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        return self.push(filter)

    def stereo_high_pass_filter(self, freq_bus: AudioInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        filter = self.synth_player.instruments.stereo_high_pass_filter(in_bus, freq_bus).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        return self.push(filter)

    def mono_low_pass_filter(self, freq_bus: AudioInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        filter = self.synth_player.instruments.mono_low_pass_filter(in_bus, freq_bus).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        return self.push(filter)

    def stereo_low_pass_filter(self, freq_bus: AudioInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        filter = self.synth_player.instruments.stereo_low_pass_filter(in_bus, freq_bus).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        return self.push(filter)

    def mono_band_pass_filter(self, freq_bus: AudioInstrument, rq_bus: AudioInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        filter = self.synth_player.instruments.mono_band_pass_filter(in_bus, freq_bus, rq_bus).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        return self.push(filter)

    def steroe_band_pass_filter(self, freq_bus: AudioInstrument, rq_bus: AudioInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        filter = (
            self.synth_player.instruments.stereo_band_pass_filter(in_bus, freq_bus, rq_bus).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        )
        return self.push(filter)

    def mono_band_reject_filter(self, freq_bus: AudioInstrument, rq_bus: AudioInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        filter = (
            self.synth_player.instruments.mono_band_reject_filter(in_bus, freq_bus, rq_bus).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        )
        return self.push(filter)

    def stereo_band_reject_filter(self, freq_bus: AudioInstrument, rq_bus: AudioInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        filter = (
            self.synth_player.instruments.stereo_band_reject_filter(in_bus, freq_bus, rq_bus).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        )
        return self.push(filter)

    def resonent_filter(self, freq_bus: AudioInstrument, decay_bus: AudioInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        filter = self.synth_player.instruments.resonant_filter(in_bus, freq_bus, decay_bus).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        return self.push(filter)

    def pan(self, pan_position: AudioInstrument) -> Self:
        in_audio = self.audio_stack.pop()
        panning = self.synth_player.instruments.panning(in_audio, pan_position).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        return self.push(panning)

    def mono_volume(self, amp: AudioInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        volume = self.synth_player.instruments.mono_volume(in_bus, amp).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        return self.push(volume)

    def stereo_volume(self, amp: AudioInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        volume = self.synth_player.instruments.stereo_volume(in_bus, amp).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        return self.push(volume)

    def stereo_hall_reverb(
        self,
        amp_bus: AudioInstrument,
        rt60: float = 1,
        stereo: float = 0.5,
        low_freq: float = 200,
        low_ratio: float = 0.5,
        hi_freq: float = 4000,
        hi_ratio: float = 0.5,
        early_diffusion: float = 0.5,
        late_diffusion: float = 0.5,
        mod_rate: float = 0.2,
        mod_depth: float = 0.3,
    ) -> Self:
        in_bus = self.audio_stack.pop()
        reverb = (
            self.synth_player.instruments
            .stereo_hall_reverb(
                in_bus,
                amp_bus,
                rt60,
                stereo,
                low_freq,
                low_ratio,
                hi_freq,
                hi_ratio,
                early_diffusion,
                late_diffusion,
                mod_rate,
                mod_depth,
            )
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        return self.push(reverb)

    def stereo_free_reverb(
        self,
        amp_bus: AudioInstrument,
        mix: float = 0.33,
        room: float = 0.5,
        damp: float = 0.5,
    ) -> Self:
        in_bus = self.audio_stack.pop()
        reverb = (
            self.synth_player.instruments.stereo_free_reverb(in_bus, amp_bus, mix, room, damp).add_action(AddAction.TAIL_ACTION).node_id(self.node_id)
        )
        return self.push(reverb)

    def stereo_g_verb(
        self,
        amp_bus: AudioInstrument,
        roomsize: float = 10,
        revtime: float = 3,
        damping: float = 0.5,
        inputbw: float = 0.5,
        spread: float = 15,
        drylevel: float = 1,
        earlyreflevel: float = 0.7,
        taillevel: float = 0.5,
    ) -> Self:
        in_bus = self.audio_stack.pop()
        reverb = (
            self.synth_player.instruments
            .stereo_g_verb(
                in_bus,
                amp_bus,
                roomsize,
                revtime,
                damping,
                inputbw,
                spread,
                drylevel,
                earlyreflevel,
                taillevel,
            )
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        return self.push(reverb)

    def handle_osc_messages(self, start_time: float, osc_messages: list[OscMessage]) -> None:
        if self.synth_player.should_send_to_score:
            for message in osc_messages:
                self.synth_player.supercollider_score.add_message(message, start_time)
        else:
            client = self.synth_player.client
            bundle = client.make_bundle(start_time, osc_messages)
            client.send_bundle(bundle)

    def play(self, start_time: float, duration: Optional[float] = None, output_bus: int = 0) -> None:
        final_duration = duration or self.audio_stack.duration
        if self.synth_player.should_send_to_score:
            final_output_bus = output_bus
        else:
            final_output_bus = output_bus % 2
        audio_graph = self.audio_stack.pop().static_output_bus(final_output_bus).build_graph(start_time, final_duration)
        osc_messages = supercollider_client.new_synths(audio_graph)
        self.handle_osc_messages(start_time, osc_messages)

    def send_to_synth_note(self, synth_note: "SynthNoteV2", start_time: float, duration: Optional[float] = None) -> None:
        final_duration = duration or self.audio_stack.duration
        assert synth_note.input is not None
        audio_graph = self.audio_stack.pop().static_output_bus(synth_note.input.get_output_bus()).build_graph(start_time, final_duration)
        osc_messages = supercollider_client.new_synths(audio_graph)
        self.handle_osc_messages(start_time, osc_messages)
