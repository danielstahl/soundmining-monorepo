from typing import Any, Self, TypeVar

from soundmining_library.bus_allocator import BusAllocator
from soundmining_library.modular.instrument import AudioInstrument, Instrument


class StaticControl(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("staticControl", 1, output_bus_allocator)
        self.value = None

    def control(self, value: float) -> Self:
        self.value = value
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.prepend_to_graph(parent)

    def internal_build(self, start_time: float, duration: float) -> list:
        return ["value", self.value]


class AbstractLineControl(AudioInstrument):
    def __init__(self, instrument_name: str, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, 1, output_bus_allocator)

    def control(self, start_value: float, end_value: float) -> Self:
        self.start_value = start_value
        self.end_value = end_value
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.prepend_to_graph(parent)

    def internal_build(self, start_time: float, duration: float) -> list:
        return ["startValue", self.start_value, "endValue", self.end_value]


class LineControl(AbstractLineControl):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("lineControl", output_bus_allocator)


class XLineControl(AbstractLineControl):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("xlineControl", output_bus_allocator)


class SineControl(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("sineControl", 1, output_bus_allocator)

    def control(self, start_value: float, peak_value: float) -> Self:
        self.start_value = start_value
        self.peak_value = peak_value
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.prepend_to_graph(parent)

    def internal_build(self, start_time: float, duration: float) -> list:
        return ["startValue", self.start_value, "peakValue", self.peak_value]


class PercControl(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("percControl", 1, output_bus_allocator)

    def control(self, start_value: float, peak_value: float, attack_time: float = 0.01, curve: float = -4) -> Self:
        self.start_value = start_value
        self.peak_value = peak_value
        self.attack_time = attack_time
        self.curve = curve
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.prepend_to_graph(parent)

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "attackTime",
            self.attack_time,
            "curve",
            self.curve,
            "startValue",
            self.start_value,
            "peakValue",
            self.peak_value,
        ]


LEVELS_T = TypeVar("LEVELS_T", bound="tuple[float, ...]")
TIMES_T = TypeVar("TIMES_T", bound="tuple[float, ...]")
CURVES_T = TypeVar("CURVES_T", bound="tuple[float, ...]")


class BlockControl(AudioInstrument):
    def __init__(self, instrument_name, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, 1, output_bus_allocator)

    def _control(self, levels: LEVELS_T, times: TIMES_T, curves: CURVES_T) -> Self:
        self.levels = levels
        self.times = times
        self.curves = curves
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.prepend_to_graph(parent)

    def internal_build(self, start_time: float, duration: float) -> list:
        return ["levels", list(self.levels), "times", list(self.times), "curves", list(self.curves)]


class BlockShapeControl(AudioInstrument):
    def __init__(self, instrument_name, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, 1, output_bus_allocator)

    def _control(self, levels: LEVELS_T, times: TIMES_T) -> Self:
        self.levels = levels
        self.times = times
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.prepend_to_graph(parent)

    def internal_build(self, start_time: float, duration: float) -> list:
        return ["levels", list(self.levels), "times", list(self.times)]


class TwoBLockControl(BlockControl):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("twoBlockControl", output_bus_allocator)

    def control(self, levels: tuple[float, float, float], times: tuple[float, float], curves: tuple[float, float]) -> Self:
        return super()._control(levels, times, curves)


class TwoBLockSineControl(BlockShapeControl):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("twoBlockSineControl", output_bus_allocator)

    def control(self, levels: tuple[float, float, float], times: tuple[float, float]) -> Self:
        return super()._control(levels, times)


class TwoBLockExpControl(BlockShapeControl):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("twoBlockExpControl", output_bus_allocator)

    def control(self, levels: tuple[float, float, float], times: tuple[float, float]) -> Self:
        return super()._control(levels, times)


class ThreeBLockControl(BlockControl):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("threeBlockControl", output_bus_allocator)

    def control(
        self,
        levels: tuple[float, float, float, float],
        times: tuple[float, float, float],
        curves: tuple[float, float, float],
    ) -> Self:
        return super()._control(levels, times, curves)


class ThreeBLockSineControl(BlockShapeControl):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("threeBlockSineControl", output_bus_allocator)

    def control(self, levels: tuple[float, float, float, float], times: tuple[float, float, float]) -> Self:
        return super()._control(levels, times)


class ThreeBLockExpControl(BlockShapeControl):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("threeBlockExpControl", output_bus_allocator)

    def control(self, levels: tuple[float, float, float, float], times: tuple[float, float, float]) -> Self:
        return super()._control(levels, times)


class FourBLockControl(BlockControl):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("fourBlockControl", output_bus_allocator)

    def control(
        self,
        levels: tuple[float, float, float, float, float],
        times: tuple[float, float, float, float],
        curves: tuple[float, float, float, float],
    ) -> Self:
        return super()._control(levels, times, curves)


class FourBLockSineControl(BlockShapeControl):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("fourBlockSineControl", output_bus_allocator)

    def control(self, levels: tuple[float, float, float, float, float], times: tuple[float, float, float, float]) -> Self:
        return super()._control(levels, times)


class FourBLockExpControl(BlockShapeControl):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("fourBlockExpControl", output_bus_allocator)

    def control(self, levels: tuple[float, float, float, float, float], times: tuple[float, float, float, float]) -> Self:
        return super()._control(levels, times)


class SignalCombine(AudioInstrument):
    def __init__(self, instrument_name: str, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, 1, output_bus_allocator)

    def combine(self, in1_bus: AudioInstrument, in2_bus: AudioInstrument) -> Self:
        self.in_bus1 = in1_bus
        self.in_bus2 = in2_bus
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.in_bus1.graph(self.in_bus2.graph(parent)))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "in1",
            self.in_bus1.dynamic_output_bus(start_time, duration),
            "in2",
            self.in_bus2.dynamic_output_bus(start_time, duration),
        ]


class SignalMix(SignalCombine):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("signalMix", output_bus_allocator)


class SignalMultiply(SignalCombine):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("signalMultiply", output_bus_allocator)


class SignalSum(SignalCombine):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("signalSum", output_bus_allocator)


class SignalShape(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("signalShape", 1, output_bus_allocator)

    def shape(self, in_bus: AudioInstrument, shape_bus: AudioInstrument) -> Self:
        self.in_bus = in_bus
        self.shape_bus = shape_bus
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.in_bus.graph(self.shape_bus.graph(parent)))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "in",
            self.in_bus.dynamic_output_bus(start_time, duration),
            "shapeBus",
            self.shape_bus.dynamic_output_bus(start_time, duration),
        ]


class OscInstrument(AudioInstrument):
    def __init__(self, instrument_name: str, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, 1, output_bus_allocator)

    def osc(self, amp_bus: AudioInstrument, freq_bus: AudioInstrument) -> Self:
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


class SawOsc(OscInstrument):
    def __init__(self, audio_bus_allocator: BusAllocator) -> None:
        super().__init__("sawOsc", audio_bus_allocator)


class DustOsc(OscInstrument):
    def __init__(self, audio_bus_allocator: BusAllocator) -> None:
        super().__init__("dustOsc", audio_bus_allocator)


class ImpulseOsc(OscInstrument):
    def __init__(self, audio_bus_allocator: BusAllocator) -> None:
        super().__init__("impulseOsc", audio_bus_allocator)


class LfNoiseInstrument(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("lfNoiseOsc", 1, output_bus_allocator)

    def lf_noise(self, amp_bus: AudioInstrument, freq_bus: AudioInstrument, low_value: float, high_value: float) -> Self:
        self.amp_bus = amp_bus
        self.freq_bus = freq_bus
        self.low_value = low_value
        self.high_value = high_value
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.amp_bus.graph(self.freq_bus.graph(parent)))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "freqBus",
            self.freq_bus.dynamic_output_bus(start_time, duration),
            "ampBus",
            self.amp_bus.dynamic_output_bus(start_time, duration),
            "lowValue",
            self.low_value,
            "highValue",
            self.high_value,
        ]


class PulseOsc(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("pulseOsc", 1, output_bus_allocator)

    def osc(self, amp_bus: AudioInstrument, freq_bus: AudioInstrument, width_bus: AudioInstrument) -> Self:
        self.amp_bus = amp_bus
        self.freq_bus = freq_bus
        self.width_bus = width_bus
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.amp_bus.graph(self.freq_bus.graph(self.width_bus.graph(parent))))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "freqBus",
            self.freq_bus.dynamic_output_bus(start_time, duration),
            "ampBus",
            self.amp_bus.dynamic_output_bus(start_time, duration),
            "widthBus",
            self.width_bus.dynamic_output_bus(start_time, duration),
        ]


class NoiseOscInstrument(AudioInstrument):
    def __init__(self, instrument_name: str, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, 1, output_bus_allocator)

    def noise(self, amp_bus: AudioInstrument) -> Self:
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


class PlayBuffer(AudioInstrument):
    def __init__(self, instrument_name: str, nr_of_channels: int, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, nr_of_channels, output_bus_allocator)

    def play_buffer(self, buf_num: int, rate: float, start: float, end: float, amp_bus: AudioInstrument) -> Self:
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

    def bank_of_resonators(self, in_bus: AudioInstrument, freqs: list[float], amps: list[float], ring_times: list[float]) -> Self:
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


class MonoGrainBuf(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("monoGrainBuf", 1, output_bus_allocator)

    def grain_buf(
        self,
        soundbuf: int,
        grain_trigger_bus: AudioInstrument,
        grain_duration_bus: AudioInstrument,
        grain_rate_bus: AudioInstrument,
        grain_pos_bus: AudioInstrument,
    ) -> Self:
        self.soundbuf = soundbuf
        self.grain_trigger_bus = grain_trigger_bus
        self.grain_duration_bus = grain_duration_bus
        self.grain_rate_bus = grain_rate_bus
        self.grain_pos_bus = grain_pos_bus
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(
            self.grain_trigger_bus.graph(self.grain_duration_bus.graph(self.grain_rate_bus.graph(self.grain_pos_bus.graph(parent))))
        )

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "soundbuf",
            self.soundbuf,
            "grainTriggerBus",
            self.grain_trigger_bus.dynamic_output_bus(start_time, duration),
            "grainDurationBus",
            self.grain_duration_bus.dynamic_output_bus(start_time, duration),
            "grainRateBus",
            self.grain_rate_bus.dynamic_output_bus(start_time, duration),
            "grainPosBus",
            self.grain_pos_bus.dynamic_output_bus(start_time, duration),
        ]


class HighPassFilter(AudioInstrument):
    def __init__(self, instrument_name: str, nr_of_channels: int, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, nr_of_channels, output_bus_allocator)

    def filter(self, in_bus: AudioInstrument, freq_bus: AudioInstrument) -> Self:
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

    def filter(self, in_bus: AudioInstrument, freq_bus: AudioInstrument) -> Self:
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

    def filter(self, in_bus: AudioInstrument, freq_bus: AudioInstrument, rq_bus: AudioInstrument) -> Self:
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

    def filter(self, in_bus: AudioInstrument, freq_bus: AudioInstrument, rq_bus: AudioInstrument) -> Self:
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


class ResonantFilter(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("resonantFilter", 1, output_bus_allocator)

    def filter(self, in_bus: AudioInstrument, freq_bus: AudioInstrument, decay_bus: AudioInstrument) -> Self:
        self.in_bus = in_bus
        self.freq_bus = freq_bus
        self.decay_bus = decay_bus
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.in_bus.graph(self.freq_bus.graph(self.decay_bus.graph(parent))))

    def internal_build(self, start_time: float, duration: float) -> list:
        return [
            "in",
            self.in_bus.dynamic_output_bus(start_time, duration),
            "freqBus",
            self.freq_bus.dynamic_output_bus(start_time, duration),
            "decayBus",
            self.decay_bus.dynamic_output_bus(start_time, duration),
        ]


class Panning(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("pan", 2, output_bus_allocator)

    def pan(self, in_bus: AudioInstrument, pan_bus: AudioInstrument) -> Self:
        self.in_bus = in_bus
        self.pan_bus = pan_bus
        return self

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return self.append_to_graph(self.in_bus.graph(self.pan_bus.graph(parent)))

    def internal_build(self, start_time: float, duration: float) -> list[Any]:
        return [
            "in",
            self.in_bus.dynamic_output_bus(start_time, duration),
            "panBus",
            self.pan_bus.dynamic_output_bus(start_time, duration),
        ]


class Volume(AudioInstrument):
    def __init__(self, instrument_name: str, nr_of_channels: int, output_bus_allocator: BusAllocator) -> None:
        super().__init__(instrument_name, nr_of_channels, output_bus_allocator)

    def volume(self, in_bus: AudioInstrument, amp_bus: AudioInstrument) -> Self:
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


class StereoHallReverb(AudioInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__("stereoHallReverb", 2, output_bus_allocator)

    def reverb(
        self,
        in_bus: AudioInstrument,
        amp_bus: AudioInstrument,
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

    def reverb(self, in_bus: AudioInstrument, amp_bus: AudioInstrument, mix: float, room: float, damp: float) -> Self:
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


class StaticAudioBusInstrument(AudioInstrument):
    def __init__(self, nr_of_channels: int, output_bus_allocator: BusAllocator) -> None:
        super().__init__("NONE", nr_of_channels, output_bus_allocator)

    def graph(self, parent: list[Instrument]) -> list[Instrument]:
        return parent

    def internal_build(self, start_time: float, duration: float) -> list[Any]:
        return []

    def build(self, start_time: float, duration: float) -> list[Any]:
        self.instrument_is_built = True
        return []


class StaticMonoAudioBusInstrument(StaticAudioBusInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__(1, output_bus_allocator)


class StaticStereoAudioBusInstrument(StaticAudioBusInstrument):
    def __init__(self, output_bus_allocator: BusAllocator) -> None:
        super().__init__(2, output_bus_allocator)


class InstrumentsV2:
    def __init__(self, audio_bus_allocator: BusAllocator) -> None:
        self.audio_bus_allocator = audio_bus_allocator

    def sine_osc(self, amp_bus: AudioInstrument, freq_bus: AudioInstrument) -> SineOsc:
        return SineOsc(self.audio_bus_allocator).osc(amp_bus, freq_bus)

    def triangle_osc(self, amp_bus: AudioInstrument, freq_bus: AudioInstrument) -> TriangleOsc:
        return TriangleOsc(self.audio_bus_allocator).osc(amp_bus, freq_bus)

    def saw_osc(self, amp_bus: AudioInstrument, freq_bus: AudioInstrument) -> SawOsc:
        return SawOsc(self.audio_bus_allocator).osc(amp_bus, freq_bus)

    def pulse_osc(self, amp_bus: AudioInstrument, freq_bus: AudioInstrument, width_bus: AudioInstrument) -> PulseOsc:
        return PulseOsc(self.audio_bus_allocator).osc(amp_bus, freq_bus, width_bus)

    def dust_osc(self, amp_bus: AudioInstrument, freq_bus: AudioInstrument) -> DustOsc:
        return DustOsc(self.audio_bus_allocator).osc(amp_bus, freq_bus)

    def impulse_osc(self, amp_bus: AudioInstrument, freq_bus: AudioInstrument) -> ImpulseOsc:
        return ImpulseOsc(self.audio_bus_allocator).osc(amp_bus, freq_bus)

    def lf_noise_osc(self, amp_bus: AudioInstrument, freq_bus: AudioInstrument, low_value: float, high_value: float) -> LfNoiseInstrument:
        return LfNoiseInstrument(self.audio_bus_allocator).lf_noise(amp_bus, freq_bus, low_value, high_value)

    def white_noise_osc(self, amp_bus: AudioInstrument) -> WhiteNoiseOsc:
        return WhiteNoiseOsc(self.audio_bus_allocator).noise(amp_bus)

    def pink_noise_osc(self, amp_bus: AudioInstrument) -> PinkNoiseOsc:
        return PinkNoiseOsc(self.audio_bus_allocator).noise(amp_bus)

    def mono_play_buffer(self, buf_num: int, rate: float, start: float, end: float, amp_bus: AudioInstrument) -> MonoPlayBuffer:
        return MonoPlayBuffer(self.audio_bus_allocator).play_buffer(buf_num, rate, start, end, amp_bus)

    def stereo_play_buffer(self, buf_num: int, rate: float, start: float, end: float, amp_bus: AudioInstrument) -> StereoPlayBuffer:
        return StereoPlayBuffer(self.audio_bus_allocator).play_buffer(buf_num, rate, start, end, amp_bus)

    def bank_of_osc(self, freqs: list[float], amps: list[float], phases: list[float]) -> BankOfOsc:
        return BankOfOsc(self.audio_bus_allocator).bank_of_osc(freqs, amps, phases)

    def bank_of_resonators(self, in_bus: AudioInstrument, freqs: list[float], amps: list[float], ring_times: list[float]) -> BankOfResonators:
        return BankOfResonators(self.audio_bus_allocator).bank_of_resonators(in_bus, freqs, amps, ring_times)

    def mono_grain_buf(
        self,
        soundbuf: int,
        grain_trigger_bus: AudioInstrument,
        grain_duration_bus: AudioInstrument,
        grain_rate_bus: AudioInstrument,
        grain_pos_bus: AudioInstrument,
    ) -> MonoGrainBuf:
        return MonoGrainBuf(self.audio_bus_allocator).grain_buf(
            soundbuf,
            grain_trigger_bus,
            grain_duration_bus,
            grain_rate_bus,
            grain_pos_bus,
        )

    def mono_high_pass_filter(self, in_bus: AudioInstrument, freq_bus: AudioInstrument) -> MonoHighPassFilter:
        return MonoHighPassFilter(self.audio_bus_allocator).filter(in_bus, freq_bus)

    def stereo_high_pass_filter(self, in_bus: AudioInstrument, freq_bus: AudioInstrument) -> StereoHighPassFilter:
        return StereoHighPassFilter(self.audio_bus_allocator).filter(in_bus, freq_bus)

    def mono_low_pass_filter(self, in_bus: AudioInstrument, freq_bus: AudioInstrument) -> MonoLowPassFilter:
        return MonoLowPassFilter(self.audio_bus_allocator).filter(in_bus, freq_bus)

    def stereo_low_pass_filter(self, in_bus: AudioInstrument, freq_bus: AudioInstrument) -> StereoLowPassFilter:
        return StereoLowPassFilter(self.audio_bus_allocator).filter(in_bus, freq_bus)

    def mono_band_pass_filter(self, in_bus: AudioInstrument, freq_bus: AudioInstrument, rq_bus: AudioInstrument) -> MonoBandPassFilter:
        return MonoBandPassFilter(self.audio_bus_allocator).filter(in_bus, freq_bus, rq_bus)

    def stereo_band_pass_filter(self, in_bus: AudioInstrument, freq_bus: AudioInstrument, rq_bus: AudioInstrument) -> StereoBandPassFilter:
        return StereoBandPassFilter(self.audio_bus_allocator).filter(in_bus, freq_bus, rq_bus)

    def mono_band_reject_filter(self, in_bus: AudioInstrument, freq_bus: AudioInstrument, rq_bus: AudioInstrument) -> MonoBandRejectFilter:
        return MonoBandRejectFilter(self.audio_bus_allocator).filter(in_bus, freq_bus, rq_bus)

    def stereo_band_reject_filter(self, in_bus: AudioInstrument, freq_bus: AudioInstrument, rq_bus: AudioInstrument) -> StereoBandRejectFilter:
        return StereoBandRejectFilter(self.audio_bus_allocator).filter(in_bus, freq_bus, rq_bus)

    def resonant_filter(self, in_bus: AudioInstrument, freq_bus: AudioInstrument, decay_bus: AudioInstrument) -> ResonantFilter:
        return ResonantFilter(self.audio_bus_allocator).filter(in_bus, freq_bus, decay_bus)

    def static_control(self, value: float) -> StaticControl:
        return StaticControl(self.audio_bus_allocator).control(value)

    def line_control(self, start_value: float, end_value: float) -> LineControl:
        return LineControl(self.audio_bus_allocator).control(start_value, end_value)

    def xline_control(self, start_value: float, end_value: float) -> XLineControl:
        return XLineControl(self.audio_bus_allocator).control(start_value, end_value)

    def sine_control(self, start_value: float, peak_value: float) -> SineControl:
        return SineControl(self.audio_bus_allocator).control(start_value, peak_value)

    def perc_control(self, start_value: float, peak_value: float, attack_time: float = 0.01, curve: float = -4) -> PercControl:
        return PercControl(self.audio_bus_allocator).control(start_value, peak_value, attack_time, curve)

    def two_block_control(self, levels: tuple[float, float, float], times: tuple[float, float], curves: tuple[float, float]) -> TwoBLockControl:
        return TwoBLockControl(self.audio_bus_allocator).control(levels, times, curves)

    def two_block_sine_control(self, levels: tuple[float, float, float], times: tuple[float, float]) -> TwoBLockSineControl:
        return TwoBLockSineControl(self.audio_bus_allocator).control(levels, times)

    def two_block_exp_control(self, levels: tuple[float, float, float], times: tuple[float, float]) -> TwoBLockExpControl:
        return TwoBLockExpControl(self.audio_bus_allocator).control(levels, times)

    def three_block_control(
        self,
        levels: tuple[float, float, float, float],
        times: tuple[float, float, float],
        curves: tuple[float, float, float],
    ) -> ThreeBLockControl:
        return ThreeBLockControl(self.audio_bus_allocator).control(levels, times, curves)

    def three_block_sine_control(self, levels: tuple[float, float, float, float], times: tuple[float, float, float]) -> ThreeBLockSineControl:
        return ThreeBLockSineControl(self.audio_bus_allocator).control(levels, times)

    def three_block_exp_control(self, levels: tuple[float, float, float, float], times: tuple[float, float, float]) -> ThreeBLockExpControl:
        return ThreeBLockExpControl(self.audio_bus_allocator).control(levels, times)

    def four_block_control(
        self,
        levels: tuple[float, float, float, float, float],
        times: tuple[float, float, float, float],
        curves: tuple[float, float, float, float],
    ) -> FourBLockControl:
        return FourBLockControl(self.audio_bus_allocator).control(levels, times, curves)

    def four_block_sine_control(
        self, levels: tuple[float, float, float, float, float], times: tuple[float, float, float, float]
    ) -> FourBLockSineControl:
        return FourBLockSineControl(self.audio_bus_allocator).control(levels, times)

    def four_block_exp_control(
        self, levels: tuple[float, float, float, float, float], times: tuple[float, float, float, float]
    ) -> FourBLockExpControl:
        return FourBLockExpControl(self.audio_bus_allocator).control(levels, times)

    def signal_mix(self, in1_bus: AudioInstrument, in2_bus: AudioInstrument) -> SignalMix:
        return SignalMix(self.audio_bus_allocator).combine(in1_bus, in2_bus)

    def signal_multiply(self, in1_bus: AudioInstrument, in2_bus: AudioInstrument) -> SignalMultiply:
        return SignalMultiply(self.audio_bus_allocator).combine(in1_bus, in2_bus)

    def signal_sum(self, in1_bus: AudioInstrument, in2_bus: AudioInstrument) -> SignalSum:
        return SignalSum(self.audio_bus_allocator).combine(in1_bus, in2_bus)

    def signal_shape(self, in_bus: AudioInstrument, shape_bus: AudioInstrument) -> SignalShape:
        return SignalShape(self.audio_bus_allocator).shape(in_bus, shape_bus)

    def panning(self, in_bus: AudioInstrument, pan_bus: AudioInstrument) -> Panning:
        return Panning(self.audio_bus_allocator).pan(in_bus, pan_bus)

    def mono_volume(self, in_bus: AudioInstrument, amp_bus: AudioInstrument) -> MonoVolume:
        return MonoVolume(self.audio_bus_allocator).volume(in_bus, amp_bus)

    def stereo_volume(self, in_bus: AudioInstrument, amp_bus: AudioInstrument) -> StereoVolume:
        return StereoVolume(self.audio_bus_allocator).volume(in_bus, amp_bus)

    def stereo_hall_reverb(
        self,
        in_bus: AudioInstrument,
        amp_bus: AudioInstrument,
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

    def stereo_free_reverb(self, in_bus: AudioInstrument, amp_bus: AudioInstrument, mix: float, room: float, damp: float) -> StereoFreeReverb:
        return StereoFreeReverb(self.audio_bus_allocator).reverb(in_bus, amp_bus, mix, room, damp)

    def stereo_g_verb(
        self,
        in_bus: AudioInstrument,
        amp_bus: AudioInstrument,
        roomsize: float = 10,
        revtime: float = 3,
        damping: float = 0.5,
        inputbw: float = 0.5,
        spread: float = 15,
        drylevel: float = 1,
        earlyreflevel: float = 0.7,
        taillevel: float = 0.5,
    ) -> StereoGVerb:
        return StereoGVerb(self.audio_bus_allocator).reverb(
            in_bus, amp_bus, roomsize, revtime, damping, inputbw, spread, drylevel, earlyreflevel, taillevel
        )

    def mono_audio_bus(self) -> StaticMonoAudioBusInstrument:
        return StaticMonoAudioBusInstrument(self.audio_bus_allocator)

    def stereo_audio_bus(self) -> StaticStereoAudioBusInstrument:
        return StaticStereoAudioBusInstrument(self.audio_bus_allocator)
