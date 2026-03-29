from soundmining_library import supercollider_client
from soundmining_library.supercollider_client import SupercolliderClient
from soundmining_library.modular.instrument import (
    AudioInstrument,
    ControlInstrument,
    AddAction,
    NodeId,
)
from soundmining_library.modular.audio_instruments import AudioInstruments
from soundmining_library.modular.control_instruments import ControlInstruments
from soundmining_library.modular.sound_play import SoundPlay, ImpulseResponse
from soundmining_library.modular.sound_play import BufNumAllocator
from soundmining_library.supercollider_score import SupercolliderScore
from pythonosc.osc_message import OscMessage
from typing import Self


class SynthPlayer:
    def __init__(
        self,
        client: SupercolliderClient,
        audio_instruments: AudioInstruments,
        control_instruments: ControlInstruments,
        buf_num_allocator: BufNumAllocator,
        buffered_playback: bool = False,
        should_send_to_score: bool = False,
    ) -> None:
        self.client = client
        self.audio_instruments = audio_instruments
        self.control_instruments = control_instruments
        self.buf_num_allocator = buf_num_allocator
        self.buffered_playback = buffered_playback
        self.sound_plays = {}
        self.impulse_responses = {}
        self.supercollider_score = SupercolliderScore()
        self.should_send_to_score = should_send_to_score

    def note(self, node_id: NodeId = NodeId.SOURCE) -> "SynthNote":
        return SynthNote(self, node_id)

    def add_sound(self, name: str, sound_path: str, start: float, end: float) -> Self:
        self.sound_plays[name] = SoundPlay(sound_path, start, end)
        return self

    def get_sound(self, name) -> SoundPlay:
        return self.sound_plays[name]

    def add_impulse_response(self, name: str, left_sound_path: str, right_sound_path: str) -> Self:
        self.impulse_responses[name] = ImpulseResponse(left_sound_path, right_sound_path)
        return self

    def get_impulse_response(self, name) -> ImpulseResponse:
        return self.impulse_responses[name]

    def start(self) -> Self:
        self.buf_num_allocator.reset()
        for sound_play in self.sound_plays.values():
            sound_play.init(self.buf_num_allocator.next(), self.client)
        for impulse_response in self.impulse_responses.values():
            impulse_response.init(self.buf_num_allocator.next(), self.buf_num_allocator.next(), self.client)
        self.supercollider_score.reset()
        return self

    def stop(self) -> Self:
        for sound_play in self.sound_plays.values():
            sound_play.stop(self.client)
        for impulse_response in self.impulse_responses.values():
            impulse_response.stop(self.client)
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


class SynthNote:
    def __init__(self, synth_player: SynthPlayer, node_id: NodeId) -> None:
        self.synth_player = synth_player
        self.audio_stack = AudioStack()
        self.input = None
        self.node_id = node_id

    def mono_input(self) -> Self:
        self.input = self.synth_player.audio_instruments.mono_audio_bus()
        self.audio_stack.push(self.input)
        return self

    def stereo_input(self) -> Self:
        self.input = self.synth_player.audio_instruments.stereo_audio_bus()
        self.audio_stack.push(self.input)
        return self

    def input_from_note(self, synth_note: "SynthNote") -> Self:
        self.input = synth_note.input
        self.audio_stack.push(self.input)
        return self

    def sound_mono(
        self,
        sound: str,
        rate: float,
        amp: ControlInstrument,
        start_override: float = None,
        end_override: float = None,
    ) -> Self:
        synth_player = self.synth_player
        sound_play = synth_player.get_sound(sound)
        start = start_override or sound_play.start
        end = end_override or sound_play.end
        mono_play_buffer = (
            synth_player.audio_instruments.mono_play_buffer(sound_play.buf_num, rate, start, end, amp)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        duration = sound_play.duration(rate)
        self.audio_stack.push(mono_play_buffer, duration)
        return self

    def sine(self, freq: ControlInstrument, amp: ControlInstrument) -> Self:
        sine = (
            self.synth_player.audio_instruments.sine_osc(amp, freq)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(sine)
        return self

    def triangle(self, freq: ControlInstrument, amp: ControlInstrument) -> Self:
        triangle = (
            self.synth_player.audio_instruments.triangle_osc(amp, freq)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(triangle)
        return self

    def pulse(self, freq: ControlInstrument, amp: ControlInstrument) -> Self:
        pulse = (
            self.synth_player.audio_instruments.pulse_osc(amp, freq)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(pulse)
        return self

    def saw(self, freq: ControlInstrument, amp: ControlInstrument) -> Self:
        saw = (
            self.synth_player.audio_instruments.saw_osc(amp, freq)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(saw)
        return self

    def dust(self, freq: ControlInstrument, amp: ControlInstrument) -> Self:
        dust = (
            self.synth_player.audio_instruments.dust_osc(amp, freq)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(dust)
        return self

    def white_noise(self, amp: ControlInstrument) -> Self:
        noise = (
            self.synth_player.audio_instruments.white_noise_osc(amp)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(noise)
        return self

    def pink_noise(self, amp: ControlInstrument) -> Self:
        noise = (
            self.synth_player.audio_instruments.pink_noise_osc(amp)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(noise)
        return self

    def bank_of_osc(self, freqs: list[float], amps: list[float], phases: list[float]) -> Self:
        bank = (
            self.synth_player.audio_instruments.bank_of_osc(freqs, amps, phases)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(bank)
        return self

    def bank_of_resonators(self, freqs: list[float], amps: list[float], ring_times: list[float]) -> Self:
        in_bus = self.audio_stack.pop()
        bank = (
            self.synth_player.audio_instruments.bank_of_resonators(in_bus, freqs, amps, ring_times)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(bank)
        return self

    def mono_high_pass_filter(self, freq_bus: ControlInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        filter = (
            self.synth_player.audio_instruments.mono_high_pass_filter(in_bus, freq_bus)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(filter)
        return self

    def stereo_high_pass_filter(self, freq_bus: ControlInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        filter = (
            self.synth_player.audio_instruments.stereo_high_pass_filter(in_bus, freq_bus)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(filter)
        return self

    def mono_low_pass_filter(self, freq_bus: ControlInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        filter = (
            self.synth_player.audio_instruments.mono_low_pass_filter(in_bus, freq_bus)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(filter)
        return self

    def stereo_low_pass_filter(self, freq_bus: ControlInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        filter = (
            self.synth_player.audio_instruments.stereo_low_pass_filter(in_bus, freq_bus)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(filter)
        return self

    def mono_band_pass_filter(self, freq_bus: ControlInstrument, rq_bus: ControlInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        filter = (
            self.synth_player.audio_instruments.mono_band_pass_filter(in_bus, freq_bus, rq_bus)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(filter)
        return self

    def steroe_band_pass_filter(self, freq_bus: ControlInstrument, rq_bus: ControlInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        filter = (
            self.synth_player.audio_instruments.stereo_band_pass_filter(in_bus, freq_bus, rq_bus)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(filter)
        return self

    def mono_band_reject_filter(self, freq_bus: ControlInstrument, rq_bus: ControlInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        filter = (
            self.synth_player.audio_instruments.mono_band_reject_filter(in_bus, freq_bus, rq_bus)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(filter)
        return self

    def stereo_band_reject_filter(self, freq_bus: ControlInstrument, rq_bus: ControlInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        filter = (
            self.synth_player.audio_instruments.stereo_band_reject_filter(in_bus, freq_bus, rq_bus)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(filter)
        return self

    def fm_sine_modulate(self, carrier_freq_bus: ControlInstrument, amp_bus: ControlInstrument) -> Self:
        modulator_bus = self.audio_stack.pop()
        modulate = (
            self.synth_player.audio_instruments.fm_sine_modulate(carrier_freq_bus, modulator_bus, amp_bus)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(modulate)
        return self

    def fm_pulse_modulate(self, carrier_freq_bus: ControlInstrument, amp_bus: ControlInstrument) -> Self:
        modulator_bus = self.audio_stack.pop()
        modulate = (
            self.synth_player.audio_instruments.fm_pulse_modulate(carrier_freq_bus, modulator_bus, amp_bus)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(modulate)
        return self

    def fm_triangle_modulate(self, carrier_freq_bus: ControlInstrument, amp_bus: ControlInstrument) -> Self:
        modulator_bus = self.audio_stack.pop()
        modulate = (
            self.synth_player.audio_instruments.fm_triangle_modulate(carrier_freq_bus, modulator_bus, amp_bus)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(modulate)
        return self

    def fm_saw_modulate(self, carrier_freq_bus: ControlInstrument, amp_bus: ControlInstrument) -> Self:
        modulator_bus = self.audio_stack.pop()
        modulate = (
            self.synth_player.audio_instruments.fm_saw_modulate(carrier_freq_bus, modulator_bus, amp_bus)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(modulate)
        return self

    def ring_modulate(self, modulater_freq_bus: ControlInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        modulate = (
            self.synth_player.audio_instruments.ring_modulate(in_bus, modulater_freq_bus)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(modulate)
        return self

    def mono_volume(self, amp: ControlInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        volume = (
            self.synth_player.audio_instruments.mono_volume(in_bus, amp)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(volume)
        return self

    def stereo_volume(self, amp: ControlInstrument) -> Self:
        in_bus = self.audio_stack.pop()
        volume = (
            self.synth_player.audio_instruments.stereo_volume(in_bus, amp)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(volume)
        return self

    def stereo_hall_reverb(
        self,
        amp_bus: ControlInstrument,
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
            self.synth_player.audio_instruments.stereo_hall_reverb(
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

        self.audio_stack.push(reverb)
        return self

    def stereo_free_reverb(
        self,
        amp_bus: ControlInstrument,
        mix: float = 0.33,
        room: float = 0.5,
        damp: float = 0.5,
    ) -> Self:
        in_bus = self.audio_stack.pop()
        reverb = (
            self.synth_player.audio_instruments.stereo_free_reverb(in_bus, amp_bus, mix, room, damp)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(reverb)
        return self

    def stereo_convolution_reverb(
        self, ir_sound: str, amp_bus: ControlInstrument, amp: float = 1.0, fft_size: int = 2048
    ) -> Self:
        impulse_response = self.synth_player.get_impulse_response(ir_sound)
        in_bus = self.audio_stack.pop()
        reverb = (
            self.synth_player.audio_instruments.stereo_convolution_reverb(
                in_bus,
                amp_bus,
                ir_left=impulse_response.left_buf_num,
                ir_right=impulse_response.right_buf_num,
                amp=amp,
                fft_size=fft_size,
            )
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(reverb)
        return self

    def stereo_g_verb(
        self,
        amp_bus: ControlInstrument,
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
            self.synth_player.audio_instruments.stereo_g_verb(
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
        self.audio_stack.push(reverb)
        return self

    def mono_comb(self, amp_bus: ControlInstrument, delay_time: float, decay_time: float) -> Self:
        in_bus = self.audio_stack.pop()
        comb = (
            self.synth_player.audio_instruments.mono_comb(in_bus, amp_bus, delay_time, decay_time)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(comb)
        return self

    def stereo_comb(self, amp_bus: ControlInstrument, delay_time: float, decay_time: float) -> Self:
        in_bus = self.audio_stack.pop()
        comb = (
            self.synth_player.audio_instruments.stereo_comb(in_bus, amp_bus, delay_time, decay_time)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(comb)
        return self

    def mono_delay(self, amp_bus: ControlInstrument, delay_time: float) -> Self:
        in_bus = self.audio_stack.pop()
        comb = (
            self.synth_player.audio_instruments.mono_delay(in_bus, amp_bus, delay_time)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(comb)
        return self

    def stereo_delay(self, amp_bus: ControlInstrument, delay_time: float) -> Self:
        in_bus = self.audio_stack.pop()
        comb = (
            self.synth_player.audio_instruments.stereo_delay(in_bus, amp_bus, delay_time)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(comb)
        return self

    def pan(self, pan_position: ControlInstrument) -> Self:
        in_audio = self.audio_stack.pop()
        panning = (
            self.synth_player.audio_instruments.panning(in_audio, pan_position)
            .add_action(AddAction.TAIL_ACTION)
            .node_id(self.node_id)
        )
        self.audio_stack.push(panning)
        return self

    def handle_osc_messages(self, start_time: float, osc_messages: list[OscMessage]) -> None:
        if self.synth_player.should_send_to_score:
            for message in osc_messages:
                self.synth_player.supercollider_score.add_message(message, start_time)
        else:
            client = self.synth_player.client
            bundle = client.make_bundle(start_time, osc_messages)
            if self.synth_player.buffered_playback:
                client.schedule_bundle(bundle)
            else:
                client.send_bundle(bundle)

    def play(self, start_time: float, duration: float = None, output_bus: int = 0) -> None:
        final_duration = duration or self.audio_stack.duration
        if not self.synth_player.should_send_to_score:
            final_output_bus = output_bus % 2
        else:
            final_output_bus = output_bus
        audio_graph = self.audio_stack.pop().static_output_bus(final_output_bus).build_graph(start_time, final_duration)
        osc_messages = supercollider_client.new_synths(audio_graph)
        self.handle_osc_messages(start_time, osc_messages)

    def send_to_synth_note(self, synth_note: "SynthNote", start_time: float, duration: float = None) -> None:
        final_duration = duration or self.audio_stack.duration

        audio_graph = (
            self.audio_stack.pop()
            .static_output_bus(synth_note.input.get_output_bus())
            .build_graph(start_time, final_duration)
        )
        osc_messages = supercollider_client.new_synths(audio_graph)
        self.handle_osc_messages(start_time, osc_messages)
