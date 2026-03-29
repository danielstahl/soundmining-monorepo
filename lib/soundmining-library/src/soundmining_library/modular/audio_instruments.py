from soundmining_library.modular.instrument import Instrument, ControlInstrument, AudioInstrument
from soundmining_library.bus_allocator import BusAllocator
from typing import Self


class OscInstrument(AudioInstrument):
    def __init__(self, instrument_name: str, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, 1, output_bus_allocator)

    def osc(self, amp_bus: ControlInstrument, freq_bus: ControlInstrument) -> Self:
        self.amp_bus = amp_bus
        self.freq_bus = freq_bus
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.amp_bus.graph(self.freq_bus.graph(parent)))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "freqBus",
            self.freq_bus.dynamic_output_bus(start_time, duration),
            "ampBus",
            self.amp_bus.dynamic_output_bus(start_time, duration),
        ]


class SineOsc(OscInstrument):
    def __init__(self, audio_bus_allocator: BusAllocator) -> None:
        super().__init__("sineOsc", audio_bus_allocator)


class TriangleOsc(OscInstrument):
    def __init__(self, audio_bus_allocator: BusAllocator) -> None:
        super().__init__("triangleOsc", audio_bus_allocator)


class PulseOsc(OscInstrument):
    def __init__(self, audio_bus_allocator: BusAllocator) -> None:
        super().__init__("pulseOsc", audio_bus_allocator)


class SawOsc(OscInstrument):
    def __init__(self, audio_bus_allocator: BusAllocator) -> None:
        super().__init__("sawOsc", audio_bus_allocator)


class DustOsc(OscInstrument):
    def __init__(self, audio_bus_allocator: BusAllocator) -> None:
        super().__init__("dustOsc", audio_bus_allocator)


class NoiseOscInstrument(AudioInstrument):
    def __init__(self, instrument_name: str, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, 1, output_bus_allocator)

    def noise(self, amp_bus: ControlInstrument) -> Self:
        self.amp_bus = amp_bus
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.amp_bus.graph(parent))

    def internal_build(self, start_time: float, duration: float) -> list:
        return ["ampBus", self.amp_bus.dynamic_output_bus(start_time, duration)]


class WhiteNoiseOsc(NoiseOscInstrument):
    def __init__(self, audio_bus_allocator: BusAllocator) -> None:
        super().__init__("whiteNoiseOsc", audio_bus_allocator)


class PinkNoiseOsc(NoiseOscInstrument):
    def __init__(self, audio_bus_allocator: BusAllocator) -> None:
        super().__init__("pinkNoiseOsc", audio_bus_allocator)


class BankOfOsc(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("bankOfOsc", 1, output_bus_allocator)

    def bank_of_osc(self, freqs: list[float], amps: list[float], phases: list[float]) -> Self:
        self.freqs = freqs
        self.amps = amps
        self.phases = phases
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(parent)

    def internal_build(self, start_time: float, duration: float) -> list:
        return ["freqs", self.freqs, "amps", self.amps, "phases", self.phases]


class BankOfResonators(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("bankOfResonators", 1, output_bus_allocator)

    def bank_of_resonators(
        self, in_bus: AudioInstrument, freqs: list[float], amps: list[float], ring_times: list[float]
    ) -> Self:
        self.in_bus = in_bus
        self.freqs = freqs
        self.amps = amps
        self.ring_times = ring_times
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.in_bus.graph(parent))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "in",
            self.in_bus.dynamic_output_bus(start_time, duration),
            "freqs",
            self.freqs,
            "amps",
            self.amps,
            "ringTimes",
            self.ring_times,
        ]


class PlayBuffer(AudioInstrument):
    def __init__(self, instrument_name: str, nr_of_channels: int, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, nr_of_channels, output_bus_allocator)

    def play_buffer(self, buf_num: int, rate: float, start: float, end: float, amp_bus: ControlInstrument) -> Self:
        self.buf_num = buf_num
        self.rate = rate
        self.start = start
        self.end = end
        self.amp_bus = amp_bus
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.amp_bus.graph(parent))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "bufNum",
            self.buf_num,
            "rate",
            self.rate,
            "start",
            self.start,
            "end",
            self.end,
            "ampBus",
            self.amp_bus.dynamic_output_bus(start_time, duration),
        ]


class MonoPlayBuffer(PlayBuffer):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("monoPlayBuffer", 1, output_bus_allocator)


class StereoPlayBuffer(PlayBuffer):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("stereoPlayBuffer", 2, output_bus_allocator)


class HighPassFilter(AudioInstrument):
    def __init__(self, instrument_name: str, nr_of_channels: int, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, nr_of_channels, output_bus_allocator)

    def filter(self, in_bus: AudioInstrument, freq_bus: ControlInstrument) -> Self:
        self.in_bus = in_bus
        self.freq_bus = freq_bus
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.in_bus.graph(self.freq_bus.graph(parent)))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "in",
            self.in_bus.dynamic_output_bus(start_time, duration),
            "freqBus",
            self.freq_bus.dynamic_output_bus(start_time, duration),
        ]


class MonoHighPassFilter(HighPassFilter):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("monoHighPassFilter", 1, output_bus_allocator)


class StereoHighPassFilter(HighPassFilter):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("stereoHighPassFilter", 2, output_bus_allocator)


class LowPassFilter(AudioInstrument):
    def __init__(self, instrument_name: str, nr_of_channels: int, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, nr_of_channels, output_bus_allocator)

    def filter(self, in_bus: AudioInstrument, freq_bus: ControlInstrument) -> Self:
        self.in_bus = in_bus
        self.freq_bus = freq_bus
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.in_bus.graph(self.freq_bus.graph(parent)))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "in",
            self.in_bus.dynamic_output_bus(start_time, duration),
            "freqBus",
            self.freq_bus.dynamic_output_bus(start_time, duration),
        ]


class MonoLowPassFilter(LowPassFilter):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("monoLowPassFilter", 1, output_bus_allocator)


class StereoLowPassFilter(LowPassFilter):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("stereoLowPassFilter", 2, output_bus_allocator)


class BandPassFilter(AudioInstrument):
    def __init__(self, instrument_name: str, nr_of_channels: int, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, nr_of_channels, output_bus_allocator)

    def filter(self, in_bus: AudioInstrument, freq_bus: ControlInstrument, rq_bus: ControlInstrument) -> Self:
        self.in_bus = in_bus
        self.freq_bus = freq_bus
        self.rq_bus = rq_bus
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.in_bus.graph(self.freq_bus.graph(self.rq_bus.graph(parent))))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "in",
            self.in_bus.dynamic_output_bus(start_time, duration),
            "freqBus",
            self.freq_bus.dynamic_output_bus(start_time, duration),
            "rqBus",
            self.rq_bus.dynamic_output_bus(start_time, duration),
        ]


class MonoBandPassFilter(BandPassFilter):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("monoBandPassFilter", 1, output_bus_allocator)


class StereoBandPassFilter(BandPassFilter):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("stereoBandPassFilter", 2, output_bus_allocator)


class BandRejectFilter(AudioInstrument):
    def __init__(self, instrument_name: str, nr_of_channels: int, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, nr_of_channels, output_bus_allocator)

    def filter(self, in_bus: AudioInstrument, freq_bus: ControlInstrument, rq_bus: ControlInstrument) -> Self:
        self.in_bus = in_bus
        self.freq_bus = freq_bus
        self.rq_bus = rq_bus
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.in_bus.graph(self.freq_bus.graph(self.rq_bus.graph(parent))))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "in",
            self.in_bus.dynamic_output_bus(start_time, duration),
            "freqBus",
            self.freq_bus.dynamic_output_bus(start_time, duration),
            "rqBus",
            self.rq_bus.dynamic_output_bus(start_time, duration),
        ]


class MonoBandRejectFilter(BandRejectFilter):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("monoBandRejectFilter", 1, output_bus_allocator)


class StereoBandRejectFilter(BandRejectFilter):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("stereoBandRejectFilter", 2, output_bus_allocator)


class FmOscModulate(AudioInstrument):
    def __init__(self, instrument_name: str, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, 1, output_bus_allocator)

    def modulate(
        self, carrier_freq_bus: ControlInstrument, modulator_bus: AudioInstrument, amp_bus: ControlInstrument
    ) -> Self:
        self.carrier_freq_bus = carrier_freq_bus
        self.modulator_bus = modulator_bus
        self.amp_bus = amp_bus
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.carrier_freq_bus.graph(self.modulator_bus.graph(self.amp_bus.graph(parent))))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "carrierFreqBus",
            self.carrier_freq_bus.dynamic_output_bus(start_time, duration),
            "modulatorBus",
            self.modulator_bus.dynamic_output_bus(start_time, duration),
            "ampBus",
            self.amp_bus.dynamic_output_bus(start_time, duration),
        ]


class FmSineModulate(FmOscModulate):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("fmSineModulate", output_bus_allocator)


class FmPulseModulate(FmOscModulate):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("fmPulseModulate", output_bus_allocator)


class FmSawModulate(FmOscModulate):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("fmSawModulate", output_bus_allocator)


class FmTriangleModulate(FmOscModulate):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("fmTriangleModulate", output_bus_allocator)


class RingModulate(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("ringModulate", 1, output_bus_allocator)

    def modulate(self, carrier_bus: AudioInstrument, modulator_freq_bus: ControlInstrument) -> Self:
        self.carrier_bus = carrier_bus
        self.modulator_freq_bus = modulator_freq_bus
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.carrier_bus.graph(self.modulator_freq_bus.graph(parent)))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "carrierBus",
            self.carrier_bus.dynamic_output_bus(start_time, duration),
            "modulatorFreqBus",
            self.modulator_freq_bus.dynamic_output_bus(start_time, duration),
        ]


class Volume(AudioInstrument):
    def __init__(self, instrument_name: str, nr_of_channels: int, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, nr_of_channels, output_bus_allocator)

    def volume(self, in_bus: AudioInstrument, amp_bus: ControlInstrument) -> Self:
        self.in_bus = in_bus
        self.amp_bus = amp_bus
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.amp_bus.graph(self.in_bus.graph(parent)))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "in",
            self.in_bus.dynamic_output_bus(start_time, duration),
            "ampBus",
            self.amp_bus.dynamic_output_bus(start_time, duration),
        ]


class MonoVolume(Volume):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("monoVolume", 1, output_bus_allocator)


class StereoVolume(Volume):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("stereoVolume", 2, output_bus_allocator)


class Comb(AudioInstrument):
    def __init__(self, instrument_name: str, nr_of_channels: int, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, nr_of_channels, output_bus_allocator)

    def comb(self, in_bus: AudioInstrument, amp_bus: ControlInstrument, delay_time: float, decay_time: float) -> Self:
        self.in_bus = in_bus
        self.amp_bus = amp_bus
        self.delay_time = delay_time
        self.decay_time = decay_time
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.amp_bus.graph(self.in_bus.graph(parent)))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "in",
            self.in_bus.dynamic_output_bus(start_time, duration),
            "ampBus",
            self.amp_bus.dynamic_output_bus(start_time, duration),
            "delaytime",
            self.delay_time,
            "decaytime",
            self.decay_time,
        ]


class MonoComb(Comb):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("monoComb", 1, output_bus_allocator)


class StereoComb(Comb):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("stereoComb", 2, output_bus_allocator)


class Delay(AudioInstrument):
    def __init__(self, instrument_name: str, nr_of_channels: int, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, nr_of_channels, output_bus_allocator)

    def delay(self, in_bus: AudioInstrument, amp_bus: ControlInstrument, delay_time: float) -> Self:
        self.in_bus = in_bus
        self.amp_bus = amp_bus
        self.delay_time = delay_time
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.amp_bus.graph(self.in_bus.graph(parent)))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "in",
            self.in_bus.dynamic_output_bus(start_time, duration),
            "ampBus",
            self.amp_bus.dynamic_output_bus(start_time, duration),
            "delaytime",
            self.delay_time,
        ]


class MonoDelay(Delay):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("monoDelay", 1, output_bus_allocator)


class StereoDelay(Delay):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("stereoDelay", 2, output_bus_allocator)


class StereoHallReverb(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("stereoHallReverb", 2, output_bus_allocator)

    def reverb(
        self,
        in_bus: AudioInstrument,
        amp_bus: ControlInstrument,
        rt60: float,
        stereo: float,
        low_freq: float,
        low_ratio: float,
        hi_freq: float,
        hi_ratio: float,
        early_diffusion: float,
        late_diffusion: float,
        mod_rate: float,
        mod_depth: float,
    ) -> Self:
        self.in_bus = in_bus
        self.amp_bus = amp_bus
        self.rt60 = rt60
        self.stereo = stereo
        self.low_freq = low_freq
        self.low_ratio = low_ratio
        self.hi_freq = hi_freq
        self.hi_ratio = hi_ratio
        self.early_diffusion = early_diffusion
        self.late_diffusion = late_diffusion
        self.mod_rate = mod_rate
        self.mod_depth = mod_depth
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.amp_bus.graph(self.in_bus.graph(parent)))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "in",
            self.in_bus.dynamic_output_bus(start_time, duration),
            "ampBus",
            self.amp_bus.dynamic_output_bus(start_time, duration),
            "rt60",
            self.rt60,
            "stereo",
            self.stereo,
            "lowFreq",
            self.low_freq,
            "lowRatio",
            self.low_ratio,
            "hiFreq",
            self.hi_freq,
            "hiRatio",
            self.hi_ratio,
            "earlyDiffusion",
            self.early_diffusion,
            "lateDiffusion",
            self.late_diffusion,
            "modRate",
            self.mod_rate,
            "modDepth",
            self.mod_depth,
        ]


class StereoFreeReverb(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("stereoFreeReverb", 2, output_bus_allocator)

    def reverb(self, in_bus: AudioInstrument, amp_bus: ControlInstrument, mix: float, room: float, damp: float) -> Self:
        self.in_bus = in_bus
        self.amp_bus = amp_bus
        self.mix = mix
        self.room = room
        self.damp = damp
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.amp_bus.graph(self.in_bus.graph(parent)))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "in",
            self.in_bus.dynamic_output_bus(start_time, duration),
            "ampBus",
            self.amp_bus.dynamic_output_bus(start_time, duration),
            "mix",
            self.mix,
            "room",
            self.room,
            "damp",
            self.damp,
        ]


class StereoGVerb(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("stereoGVerb", 2, output_bus_allocator)

    def reverb(
        self,
        in_bus: AudioInstrument,
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
        self.in_bus = in_bus
        self.amp_bus = amp_bus
        self.roomsize = roomsize
        self.revtime = revtime
        self.damping = damping
        self.inputbw = inputbw
        self.spread = spread
        self.drylevel = drylevel
        self.earlyreflevel = earlyreflevel
        self.taillevel = taillevel
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.amp_bus.graph(self.in_bus.graph(parent)))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "in",
            self.in_bus.dynamic_output_bus(start_time, duration),
            "ampBus",
            self.amp_bus.dynamic_output_bus(start_time, duration),
            "roomsize",
            self.roomsize,
            "revtime",
            self.revtime,
            "damping",
            self.damping,
            "inputbw",
            self.inputbw,
            "spread",
            self.spread,
            "drylevel",
            self.drylevel,
            "earlyreflevel",
            self.earlyreflevel,
            "taillevel",
            self.taillevel,
        ]


class StereoConvolutionReverb(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("stereoConvolutionReverb", 2, output_bus_allocator)

    def reverb(
        self,
        in_bus: AudioInstrument,
        amp_bus: ControlInstrument,
        ir_left: int,
        ir_right: int,
        amp: float = 1.0,
        fft_size: int = 2048,
    ) -> Self:
        self.in_bus = in_bus
        self.amp_bus = amp_bus
        self.ir_left = ir_left
        self.ir_right = ir_right
        self.amp = amp
        self.fft_size = fft_size
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.amp_bus.graph(self.in_bus.graph(parent)))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "in",
            self.in_bus.dynamic_output_bus(start_time, duration),
            "ampBus",
            self.amp_bus.dynamic_output_bus(start_time, duration),
            "fftSize",
            self.fft_size,
            "irLeft",
            self.ir_left,
            "irRight",
            self.ir_right,
            "amp",
            self.amp,
        ]


class Panning(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("pan", 2, output_bus_allocator)

    def pan(self, in_bus: AudioInstrument, pan_bus: ControlInstrument) -> Self:
        self.in_bus = in_bus
        self.pan_bus = pan_bus
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.in_bus.graph(self.pan_bus.graph(parent)))

    def internal_build(self, start_time: float, duration: float) -> list[any]:
        return [
            "in",
            self.in_bus.dynamic_output_bus(start_time, duration),
            "panBus",
            self.pan_bus.dynamic_output_bus(start_time, duration),
        ]


class StaticAudioBusInstrument(AudioInstrument):
    def __init__(self, nr_of_channels: int, output_bus_allocator: BusAllocator) -> None:
        super().__init__("NONE", nr_of_channels, output_bus_allocator)

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return parent

    def internal_build(self, start_time: float, duration: float) -> list[any]:
        return []

    def build(self, start_time: float, duration: float) -> list[any]:
        self.instrument_is_built = True
        return []


class StaticMonoAudioBusInstrument(StaticAudioBusInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__(1, output_bus_allocator)


class StaticStereoAudioBusInstrument(StaticAudioBusInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__(2, output_bus_allocator)


class AudioInstruments:
    def __init__(self, audio_bus_allocator: BusAllocator) -> None:
        self.audio_bus_allocator = audio_bus_allocator

    def sine_osc(self, amp_bus: ControlInstrument, freq_bus: ControlInstrument) -> SineOsc:
        return SineOsc(self.audio_bus_allocator).osc(amp_bus, freq_bus)

    def triangle_osc(self, amp_bus: ControlInstrument, freq_bus: ControlInstrument) -> TriangleOsc:
        return TriangleOsc(self.audio_bus_allocator).osc(amp_bus, freq_bus)

    def pulse_osc(self, amp_bus: ControlInstrument, freq_bus: ControlInstrument) -> PulseOsc:
        return PulseOsc(self.audio_bus_allocator).osc(amp_bus, freq_bus)

    def saw_osc(self, amp_bus: ControlInstrument, freq_bus: ControlInstrument) -> SawOsc:
        return SawOsc(self.audio_bus_allocator).osc(amp_bus, freq_bus)

    def dust_osc(self, amp_bus: ControlInstrument, freq_bus: ControlInstrument) -> DustOsc:
        return DustOsc(self.audio_bus_allocator).osc(amp_bus, freq_bus)

    def white_noise_osc(self, amp_bus: ControlInstrument) -> WhiteNoiseOsc:
        return WhiteNoiseOsc(self.audio_bus_allocator).noise(amp_bus)

    def pink_noise_osc(self, amp_bus: ControlInstrument) -> PinkNoiseOsc:
        return PinkNoiseOsc(self.audio_bus_allocator).noise(amp_bus)

    def bank_of_osc(self, freqs: list[float], amps: list[float], phases: list[float]) -> BankOfOsc:
        return BankOfOsc(self.audio_bus_allocator).bank_of_osc(freqs, amps, phases)

    def bank_of_resonators(
        self, in_bus: AudioInstrument, freqs: list[float], amps: list[float], ring_times: list[float]
    ) -> BankOfResonators:
        return BankOfResonators(self.audio_bus_allocator).bank_of_resonators(in_bus, freqs, amps, ring_times)

    def mono_play_buffer(
        self, buf_num: int, rate: float, start: float, end: float, amp_bus: ControlInstrument
    ) -> MonoPlayBuffer:
        return MonoPlayBuffer(self.audio_bus_allocator).play_buffer(buf_num, rate, start, end, amp_bus)

    def stereo_play_buffer(
        self, buf_num: int, rate: float, start: float, end: float, amp_bus: ControlInstrument
    ) -> StereoPlayBuffer:
        return StereoPlayBuffer(self.audio_bus_allocator).play_buffer(buf_num, rate, start, end, amp_bus)

    def mono_high_pass_filter(self, in_bus: AudioInstrument, freq_bus: ControlInstrument) -> MonoHighPassFilter:
        return MonoHighPassFilter(self.audio_bus_allocator).filter(in_bus, freq_bus)

    def stereo_high_pass_filter(self, in_bus: AudioInstrument, freq_bus: ControlInstrument) -> StereoHighPassFilter:
        return StereoHighPassFilter(self.audio_bus_allocator).filter(in_bus, freq_bus)

    def mono_low_pass_filter(self, in_bus: AudioInstrument, freq_bus: ControlInstrument) -> MonoLowPassFilter:
        return MonoLowPassFilter(self.audio_bus_allocator).filter(in_bus, freq_bus)

    def stereo_low_pass_filter(self, in_bus: AudioInstrument, freq_bus: ControlInstrument) -> StereoLowPassFilter:
        return StereoLowPassFilter(self.audio_bus_allocator).filter(in_bus, freq_bus)

    def mono_band_pass_filter(
        self, in_bus: AudioInstrument, freq_bus: ControlInstrument, rq_bus: ControlInstrument
    ) -> MonoBandPassFilter:
        return MonoBandPassFilter(self.audio_bus_allocator).filter(in_bus, freq_bus, rq_bus)

    def stereo_band_pass_filter(
        self, in_bus: AudioInstrument, freq_bus: ControlInstrument, rq_bus: ControlInstrument
    ) -> StereoBandPassFilter:
        return StereoBandPassFilter(self.audio_bus_allocator).filter(in_bus, freq_bus, rq_bus)

    def mono_band_reject_filter(
        self, in_bus: AudioInstrument, freq_bus: ControlInstrument, rq_bus: ControlInstrument
    ) -> MonoBandRejectFilter:
        return MonoBandRejectFilter(self.audio_bus_allocator).filter(in_bus, freq_bus, rq_bus)

    def stereo_band_reject_filter(
        self, in_bus: AudioInstrument, freq_bus: ControlInstrument, rq_bus: ControlInstrument
    ) -> StereoBandRejectFilter:
        return StereoBandRejectFilter(self.audio_bus_allocator).filter(in_bus, freq_bus, rq_bus)

    def fm_sine_modulate(
        self, carrier_freq_bus: ControlInstrument, modulator_bus: AudioInstrument, amp_bus: ControlInstrument
    ) -> FmSineModulate:
        return FmSineModulate(self.audio_bus_allocator).modulate(carrier_freq_bus, modulator_bus, amp_bus)

    def fm_pulse_modulate(
        self, carrier_freq_bus: ControlInstrument, modulator_bus: AudioInstrument, amp_bus: ControlInstrument
    ) -> FmSineModulate:
        return FmPulseModulate(self.audio_bus_allocator).modulate(carrier_freq_bus, modulator_bus, amp_bus)

    def fm_saw_modulate(
        self, carrier_freq_bus: ControlInstrument, modulator_bus: AudioInstrument, amp_bus: ControlInstrument
    ) -> FmSineModulate:
        return FmSawModulate(self.audio_bus_allocator).modulate(carrier_freq_bus, modulator_bus, amp_bus)

    def fm_triangle_modulate(
        self, carrier_freq_bus: ControlInstrument, modulator_bus: AudioInstrument, amp_bus: ControlInstrument
    ) -> FmSineModulate:
        return FmTriangleModulate(self.audio_bus_allocator).modulate(carrier_freq_bus, modulator_bus, amp_bus)

    def ring_modulate(self, carrier_bus: AudioInstrument, modulator_freq_bus: ControlInstrument) -> RingModulate:
        return RingModulate(self.audio_bus_allocator).modulate(carrier_bus, modulator_freq_bus)

    def mono_volume(self, in_bus: AudioInstrument, amp_bus: ControlInstrument) -> MonoVolume:
        return MonoVolume(self.audio_bus_allocator).volume(in_bus, amp_bus)

    def stereo_volume(self, in_bus: AudioInstrument, amp_bus: ControlInstrument) -> StereoVolume:
        return StereoVolume(self.audio_bus_allocator).volume(in_bus, amp_bus)

    def stereo_hall_reverb(
        self,
        in_bus: AudioInstrument,
        amp_bus: ControlInstrument,
        rt60: float,
        stereo: float,
        low_freq: float,
        low_ratio: float,
        hi_freq: float,
        hi_ratio: float,
        early_diffusion: float,
        late_diffusion: float,
        mod_rate: float,
        mod_depth: float,
    ) -> StereoHallReverb:
        return StereoHallReverb(self.audio_bus_allocator).reverb(
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

    def stereo_free_reverb(
        self, in_bus: AudioInstrument, amp_bus: ControlInstrument, mix: float, room: float, damp: float
    ) -> StereoFreeReverb:
        return StereoFreeReverb(self.audio_bus_allocator).reverb(in_bus, amp_bus, mix, room, damp)

    def stereo_g_verb(
        self,
        in_bus: AudioInstrument,
        amp_bus: ControlInstrument,
        roomsize: float = 10,
        revtime: float = 3,
        damping: float = 0.5,
        inputbw: float = 0.5,
        spread: float = 15,
        drylevel: float = 1,
        earlyreflevel: float = 0.7,
        taillevel: float = 0.5,
    ) -> StereoFreeReverb:
        return StereoGVerb(self.audio_bus_allocator).reverb(
            in_bus, amp_bus, roomsize, revtime, damping, inputbw, spread, drylevel, earlyreflevel, taillevel
        )

    def stereo_convolution_reverb(
        self,
        in_bus: AudioInstrument,
        amp_bus: ControlInstrument,
        ir_left: int,
        ir_right: int,
        amp: float = 1.0,
        fft_size: int = 2048,
    ) -> StereoConvolutionReverb:
        return StereoConvolutionReverb(self.audio_bus_allocator).reverb(
            in_bus, amp_bus, ir_left, ir_right, amp, fft_size
        )

    def mono_comb(
        self, in_bus: AudioInstrument, amp_bus: ControlInstrument, delay_time: float, decay_time: float
    ) -> MonoComb:
        return MonoComb(self.audio_bus_allocator).comb(in_bus, amp_bus, delay_time, decay_time)

    def stereo_comb(
        self, in_bus: AudioInstrument, amp_bus: ControlInstrument, delay_time: float, decay_time: float
    ) -> StereoComb:
        return StereoComb(self.audio_bus_allocator).comb(in_bus, amp_bus, delay_time, decay_time)

    def mono_delay(self, in_bus: AudioInstrument, amp_bus: ControlInstrument, delay_time: float) -> MonoDelay:
        return MonoDelay(self.audio_bus_allocator).delay(in_bus, amp_bus, delay_time)

    def stereo_delay(self, in_bus: AudioInstrument, amp_bus: ControlInstrument, delay_time: float) -> StereoDelay:
        return StereoDelay(self.audio_bus_allocator).delay(in_bus, amp_bus, delay_time)

    def panning(self, in_bus: AudioInstrument, pan_bus: ControlInstrument) -> Panning:
        return Panning(self.audio_bus_allocator).pan(in_bus, pan_bus)

    def mono_audio_bus(self) -> StaticMonoAudioBusInstrument:
        return StaticMonoAudioBusInstrument(self.audio_bus_allocator)

    def stereo_audio_bus(self) -> StaticStereoAudioBusInstrument:
        return StaticStereoAudioBusInstrument(self.audio_bus_allocator)
