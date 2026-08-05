import random
from enum import StrEnum

from soundmining_library.generative import random_int_range, random_range
from soundmining_library.modular.instrument import AddAction, AudioInstrument
from soundmining_library.piece import Piece
from soundmining_library.sound_data import SoundData
from soundmining_library.spectrum import make_fact, make_spectrum, make_undertone_spectrum

Sounds = StrEnum("Sounds", ["H1", "H2", "K1", "Ka1", "Ki1", "Ko1", "S1", "S2"])


class ConcreteMusic16:
    def __init__(self, piece: Piece) -> None:
        self._piece = piece
        self._all_sound_data = self._build_sound_data(piece)
        self._static_control = piece.instruments.static_control
        self._sine_control = piece.instruments.sine_control
        self._line_control = piece.instruments.line_control
        self._two_block_sine_control = piece.instruments.two_block_sine_control
        self._impulse_osc = piece.instruments.impulse_osc
        self._dust_osc = piece.instruments.dust_osc
        self._signal_sum = piece.instruments.signal_sum
        self._signal_multiply = piece.instruments.signal_multiply
        self._lf_noise_osc = piece.instruments.lf_noise_osc
        self._s2_sound_data = self._all_sound_data[Sounds.S2]
        self._setup_spectral_data()

    def _build_sound_data(self, piece: Piece) -> dict[Sounds, SoundData]:
        SOUNDPATH = piece.environment.sound_path
        return {
            Sounds.H1: SoundData.from_analysis(
                sound=Sounds.H1,
                file_name=f"{SOUNDPATH}/H1.aif",
            ),
            Sounds.H2: SoundData.from_analysis(
                sound=Sounds.H2,
                file_name=f"{SOUNDPATH}/H2.aif",
            ),
            Sounds.K1: SoundData.from_analysis(
                sound=Sounds.K1,
                file_name=f"{SOUNDPATH}/K1.aif",
            ),
            Sounds.Ka1: SoundData.from_analysis(
                sound=Sounds.Ka1,
                file_name=f"{SOUNDPATH}/Ka1.aif",
            ),
            Sounds.Ki1: SoundData.from_analysis(
                sound=Sounds.Ki1,
                file_name=f"{SOUNDPATH}/Ki1.aif",
            ),
            Sounds.Ko1: SoundData.from_analysis(
                sound=Sounds.Ko1,
                file_name=f"{SOUNDPATH}/Ko1.aif",
            ),
            Sounds.S1: SoundData.from_analysis(
                sound=Sounds.S1,
                file_name=f"{SOUNDPATH}/S1.aif",
            ),
            Sounds.S2: SoundData.from_analysis(
                sound=Sounds.S2,
                file_name=f"{SOUNDPATH}/S2.aif",
            ),
        }

    def _setup_spectral_data(self):
        s2_sound_data = self._all_sound_data[Sounds.S2]
        self._s2_sound_data = s2_sound_data
        # High, Low
        fundamental1 = 1
        first_partial1 = 3
        start_partial1 = 1

        # High
        fundamental2 = 0
        first_partial2 = 1
        start_partial2 = 2

        # Low
        fundamental3 = 0
        first_partial3 = 3
        start_partial3 = 2

        self._fact1 = make_fact(s2_sound_data.partials[fundamental1].frequency, s2_sound_data.partials[first_partial1].frequency)

        self._overtone_spectrum1 = make_spectrum(s2_sound_data.partials[start_partial1].frequency, self._fact1, 50)
        self._undertone_spectrum1 = make_undertone_spectrum(s2_sound_data.partials[start_partial1].frequency, self._fact1, 50)

        self._fact2 = make_fact(s2_sound_data.partials[fundamental2].frequency, s2_sound_data.partials[first_partial2].frequency)
        self._overtone_spectrum2 = make_spectrum(s2_sound_data.partials[start_partial2].frequency, self._fact2, 50)

        self._fact3 = make_fact(s2_sound_data.partials[fundamental3].frequency, s2_sound_data.partials[first_partial3].frequency)
        self._undertone_spectrum3 = make_undertone_spectrum(s2_sound_data.partials[start_partial3].frequency, self._fact3, 50)

    @staticmethod
    def _get_variable_start_end(the_arg: float | tuple[float, float] | None) -> tuple[float, float]:
        match the_arg:
            case (start, end):
                start = start
                end = end
            case float(val) | int(val):
                start = val
                end = val

        return (start, end)

    def make_grain_trigger_bus(
        self, impulse_freq: float | tuple[float, float] | None, dust_freq: float | tuple[float, float] | None = None
    ) -> AudioInstrument:
        impulse_start, impulse_end = ConcreteMusic16._get_variable_start_end(impulse_freq)
        if impulse_start:
            impulse_trigger = self._impulse_osc(
                amp_bus=self._static_control(1.0), freq_bus=self._line_control(impulse_start, impulse_end)
            ).add_action(AddAction.TAIL_ACTION)

        if dust_freq:
            dust_start, dust_end = ConcreteMusic16._get_variable_start_end(dust_freq)
            dust_trigger = self._dust_osc(amp_bus=self._static_control(1.0), freq_bus=self._line_control(dust_start, dust_end)).add_action(
                AddAction.TAIL_ACTION
            )
        else:
            dust_trigger = None

        match (impulse_trigger, dust_trigger):
            case (imp, dust) if imp is not None and dust is not None:
                return self._signal_sum(imp, dust).add_action(AddAction.TAIL_ACTION)
            case (imp, None) if imp is not None:
                return imp
            case (None, dust) if dust is not None:
                return dust
            case _:
                raise TypeError("Dead match")

    def make_grain_duration_bus(
        self,
        grain_duration: float | tuple[float, float],
        grain_duration_noise: float | tuple[float, float] | None = None,
        lf_noise_rate: float = 500,
    ) -> AudioInstrument:
        grain_duration_start, grain_duration_end = ConcreteMusic16._get_variable_start_end(grain_duration)
        grain_duration_line = self._line_control(grain_duration_start, grain_duration_end).add_action(AddAction.TAIL_ACTION)
        match grain_duration_noise:
            case (noise_lower, noise_upper):
                grain_duration_lf_noise = self._lf_noise_osc(
                    amp_bus=self._static_control(1.0),
                    freq_bus=self._static_control(lf_noise_rate),
                    low_value=noise_lower,
                    high_value=noise_upper,
                ).add_action(AddAction.TAIL_ACTION)
            case float(noise_val) | int(noise_val):
                grain_duration_lf_noise = self._lf_noise_osc(
                    amp_bus=self._static_control(1.0),
                    freq_bus=self._static_control(lf_noise_rate),
                    low_value=noise_val if noise_val < 1.0 else 1.0,
                    high_value=noise_val if noise_val > 1.0 else 1.0,
                ).add_action(AddAction.TAIL_ACTION)
            case None:
                grain_duration_lf_noise = None

        if grain_duration_lf_noise is not None:
            return self._signal_multiply(grain_duration_line, grain_duration_lf_noise).add_action(AddAction.TAIL_ACTION)
        else:
            return grain_duration_line

    def make_grain_rate_bus(
        self,
        grain_rate: float | tuple[float, float],
        grain_rate_noise: float | tuple[float, float] | None = None,
        lf_noise_rate: float = 500,
    ) -> AudioInstrument:
        grain_rate_start, grain_rate_end = ConcreteMusic16._get_variable_start_end(grain_rate)
        grain_rate_line = self._line_control(grain_rate_start, grain_rate_end).add_action(AddAction.TAIL_ACTION)
        match grain_rate_noise:
            case (noise_lower, noise_upper):
                grain_rate_lf_noise = self._lf_noise_osc(
                    amp_bus=self._static_control(1.0),
                    freq_bus=self._static_control(lf_noise_rate),
                    low_value=noise_lower,
                    high_value=noise_upper,
                ).add_action(AddAction.TAIL_ACTION)
            case float(noise_val) | int(noise_val):
                grain_rate_lf_noise = self._lf_noise_osc(
                    amp_bus=self._static_control(1.0),
                    freq_bus=self._static_control(lf_noise_rate),
                    low_value=noise_val if noise_val < 1.0 else 1.0,
                    high_value=noise_val if noise_val > 1.0 else 1.0,
                ).add_action(AddAction.TAIL_ACTION)
            case None:
                grain_rate_lf_noise = None

        if grain_rate_lf_noise is not None:
            return self._signal_multiply(grain_rate_line, grain_rate_lf_noise).add_action(AddAction.TAIL_ACTION)
        else:
            return grain_rate_line

    def make_grain_pos_bus(
        self,
        sound_data: SoundData,
        reversed: bool,
        grain_pos_noise: float | tuple[float, float] | None = None,
        lf_noise_rate: float = 500,
    ) -> AudioInstrument:
        relative_start, relative_end = sound_data.get_relative_start_end()

        if reversed:
            pos_end = relative_start
            pos_start = relative_end
        else:
            pos_start = relative_start
            pos_end = relative_end

        line_pos = self._line_control(pos_start, pos_end).add_action(AddAction.TAIL_ACTION)

        match grain_pos_noise:
            case (noise_lower, noise_upper):
                grain_pos_lf_noise = self._lf_noise_osc(
                    amp_bus=self._static_control(1.0),
                    freq_bus=self._static_control(lf_noise_rate),
                    low_value=noise_lower,
                    high_value=noise_upper,
                ).add_action(AddAction.TAIL_ACTION)
            case float(noise_val) | int(noise_val):
                grain_pos_lf_noise = self._lf_noise_osc(
                    amp_bus=self._static_control(1.0),
                    freq_bus=self._static_control(lf_noise_rate),
                    low_value=noise_val * -1.0,
                    high_value=noise_val,
                ).add_action(AddAction.TAIL_ACTION)
            case None:
                grain_pos_lf_noise = None

        if grain_pos_lf_noise is not None:
            return self._signal_sum(line_pos, grain_pos_lf_noise).add_action(AddAction.TAIL_ACTION)
        else:
            return line_pos

    def play_sound_with_grainbuf(
        self,
        start: float,
        sound_data: SoundData,
        grain_pos_bus: AudioInstrument,
        pan_position: AudioInstrument,
        grain_trigger_bus: AudioInstrument,
        grain_duration_bus: AudioInstrument,
        grain_rate_bus: AudioInstrument,
        volume: float,
        play_rate: float,
        output_bus: int,
    ):
        sound = sound_data.sound

        duration = sound_data.get_play_duration(play_rate)
        (
            self._piece.synth_player
            .note()
            .mono_grain_buf(sound, grain_trigger_bus, grain_duration_bus, grain_rate_bus, grain_pos_bus)
            .mono_volume(self._sine_control(0, volume))
            .pan(pan_position)
            .play(start_time=start, duration=duration, output_bus=output_bus)
        )

    def play_high_pad1(
        self, start: float, note: int, amp: float, sound_data: SoundData, overtone_spectrum: list[float], rate_note: int, play_rate: float
    ):

        note_freq = overtone_spectrum[note]
        grain_pos_bus = self.make_grain_pos_bus(sound_data=sound_data, reversed=False, grain_pos_noise=None)
        pan_position = self._line_control(random_range(-0.99, 0.99), random_range(-0.99, 0.99))
        dust_freq = random_range(5, 10)
        grain_trigger_bus = self.make_grain_trigger_bus(impulse_freq=note_freq, dust_freq=dust_freq)
        avg_trigger_freq = (note_freq + dust_freq) / 2
        # grain_duration = (1 / avg_trigger_freq) * random_range(3.0, 10.0)
        grain_duration = (1 / avg_trigger_freq) * random_range(20.0, 30.0)
        # grain_duration = (1 / avg_trigger_freq) * random_range(15.0, 25.0)
        # grain_duration_noise = 10.0
        grain_duration_noise = 5.0
        # grain_duration_noise = None
        grain_duration_bus = self.make_grain_duration_bus(grain_duration=grain_duration, grain_duration_noise=grain_duration_noise)
        rate = sound_data.make_rate(overtone_spectrum[rate_note])
        grain_rate_bus = self.make_grain_rate_bus(grain_rate=rate, grain_rate_noise=None)
        volume = amp * 4.0

        self.play_sound_with_grainbuf(
            start=start,
            sound_data=sound_data,
            grain_pos_bus=grain_pos_bus,
            pan_position=pan_position,
            grain_trigger_bus=grain_trigger_bus,
            grain_duration_bus=grain_duration_bus,
            grain_rate_bus=grain_rate_bus,
            volume=volume,
            play_rate=play_rate,
            output_bus=0,
        )

    def play_low_pad1(
        self, start: float, note: int, amp: float, sound_data: SoundData, undertone_spectrum: list[float], rate_note: int, play_rate: float
    ):

        note_freq = undertone_spectrum[note]
        grain_pos_bus = self.make_grain_pos_bus(sound_data=sound_data, reversed=False, grain_pos_noise=None)
        pan_position = self._line_control(random_range(-0.99, 0.99), random_range(-0.99, 0.99))
        dust_freq = random_range(5, 10)
        grain_trigger_bus = self.make_grain_trigger_bus(impulse_freq=note_freq, dust_freq=dust_freq)
        avg_trigger_freq = (note_freq + dust_freq) / 2
        # grain_duration = (1 / avg_trigger_freq) * random_range(3.0, 10.0)
        grain_duration = (1 / avg_trigger_freq) * random_range(20.0, 30.0)
        # grain_duration_noise = 6.0
        grain_duration_noise = None
        grain_duration_bus = self.make_grain_duration_bus(grain_duration=grain_duration, grain_duration_noise=grain_duration_noise)
        # rate_note = 3
        # rate_note = 0
        rate = sound_data.make_rate(undertone_spectrum[rate_note])
        grain_rate_bus = self.make_grain_rate_bus(grain_rate=rate, grain_rate_noise=None)
        # volume = amp * 4.0
        volume = amp * 4.0

        self.play_sound_with_grainbuf(
            start=start,
            sound_data=sound_data,
            grain_pos_bus=grain_pos_bus,
            pan_position=pan_position,
            grain_trigger_bus=grain_trigger_bus,
            grain_duration_bus=grain_duration_bus,
            grain_rate_bus=grain_rate_bus,
            volume=volume,
            play_rate=play_rate,
            output_bus=0,
        )

    def play_high_pad_melody1(self, start: float):
        melody_duration = 5
        time = start
        reverse = random.choice([True, False])
        rate_note_start, rate_note_end = (30, 10) if reverse else (10, 30)

        while time < (start + melody_duration):
            note = random_int_range(0, 6)
            amp = random_range(0.15, 0.85)
            play_rate = random_range(1, 3)
            progress = min((time - start) / melody_duration, 1.0)
            rate_note = round(rate_note_start + progress * (rate_note_end - rate_note_start))
            self.play_high_pad1(time, note, amp, self._s2_sound_data, self._overtone_spectrum1, rate_note, play_rate)
            time += random_range(0.5, 1)

    def play_low_pad_melody1(self, start: float):
        melody_duration = 45
        time = start
        reverse = random.choice([True, False])
        rate_note_start, rate_note_end = (2, 10) if reverse else (10, 2)
        while time < (start + melody_duration):
            note = random_int_range(0, 11)
            amp = random_range(0.15, 0.85)
            play_rate = random_range(8, 13)
            progress = min((time - start) / melody_duration, 1.0)
            rate_note = round(rate_note_start + progress * (rate_note_end - rate_note_start))
            self.play_low_pad1(time, note, amp, self._s2_sound_data, self._undertone_spectrum1, rate_note, play_rate)
            time += random_range(3, 5)

    def play_low_pad_melody2(self, start: float):
        melody_duration = 60
        time = start
        reverse = random.choice([True, False])
        rate_note_start, rate_note_end = (20, 40) if reverse else (40, 20)
        while time < (start + melody_duration):
            note = random_int_range(7, 20)
            amp = random_range(0.15, 0.85)
            play_rate = random_range(8, 13)
            progress = min((time - start) / melody_duration, 1.0)
            rate_note = round(rate_note_start + progress * (rate_note_end - rate_note_start))
            self.play_low_pad1(time, note, amp, self._s2_sound_data, self._undertone_spectrum1, rate_note, play_rate)
            time += random_range(5, 8)
