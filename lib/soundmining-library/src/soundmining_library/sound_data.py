from dataclasses import dataclass, field
from enum import StrEnum

import librosa
import numpy as np
from scipy.signal import find_peaks

from soundmining_library.modular_v2.synth_player_v2 import SynthPlayerV2
from soundmining_library.spectrum import make_fact, make_spectrum, make_undertone_spectrum


def analyze_timing(
    y: np.ndarray,
    sr: int,
    threshold_db: float = -40.0,
    hop_length: int = 256,
    max_gap_ms: float = 30.0,
) -> dict:
    """
    Determine start_time / end_time via an amplitude (RMS) threshold, and
    peak_time as the point of maximum RMS energy.

    Crucially, start_time/end_time are the contiguous active region *around
    the peak*, not simply the first/last frame anywhere in the file that
    crosses the threshold. A spurious loud moment elsewhere in the
    recording (a click, a mic bump, room noise) separated from the real
    sound by clean silence must NOT be allowed to pull the analysis window
    open to include it -- which a naive first/last-above-threshold approach
    would do. max_gap_ms allows bridging brief within-sound dips (e.g. a
    short dip in a decay tail) without treating them as the sound's edge;
    it is deliberately much shorter than the kind of silence gap that would
    separate genuinely unrelated events.

    threshold_db is relative to the loudest point in the file. -40dB is a
    reasonable default for percussive/concrete sounds with a clear attack;
    lower it (e.g. -50) for soft/slow-onset sounds, raise it (e.g. -30) if
    room noise or tape hiss is being caught as part of the sound.
    """
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

    peak_frame = int(np.argmax(rms))
    max_gap_frames = max(1, int(round((max_gap_ms / 1000.0) * sr / hop_length)))

    above = rms_db > threshold_db

    start_frame = peak_frame
    gap = 0
    i = peak_frame
    while i > 0:
        i -= 1
        if above[i]:
            start_frame = i
            gap = 0
        else:
            gap += 1
            if gap > max_gap_frames:
                break

    end_frame = peak_frame
    gap = 0
    i = peak_frame
    while i < len(above) - 1:
        i += 1
        if above[i]:
            end_frame = i
            gap = 0
        else:
            gap += 1
            if gap > max_gap_frames:
                break

    start_time = times[start_frame]
    end_time = times[end_frame]
    peak_time = times[peak_frame]

    return {
        "start_time": round(float(start_time), 3),
        "end_time": round(float(end_time), 3),
        "peak_time": round(float(peak_time), 3),
        "duration": round(float(len(y) / sr), 3),
        "_peak_frame": peak_frame,
        "_hop_length": hop_length,
    }


def summarize_partials(trajectories: list[dict]) -> dict:
    """
    Derive fundamental/first_partial/peaks/peak_amplitudes directly from
    partial trajectories, so these numbers are guaranteed to describe the
    exact same set of detected partials as --trajectories output -- rather
    than being computed from a separate, independently-filtered snapshot
    that can (and did) disagree with the trajectory list on which partials
    exist at all.
    """
    if not trajectories:
        return {"fundamental": 0.0, "first_partial": 0.0, "peaks": [], "peak_amplitudes": []}

    by_amp = sorted(trajectories, key=lambda p: p["relative_amp"], reverse=True)
    fundamental = by_amp[0]["freq"]
    first_partial = by_amp[1]["freq"] if len(by_amp) > 1 else fundamental

    by_freq = sorted(trajectories, key=lambda p: p["freq"])
    return {
        "fundamental": fundamental,
        "first_partial": first_partial,
        "peaks": [p["freq"] for p in by_freq],
        "peak_amplitudes": [p["relative_amp"] for p in by_freq],
    }


def analyze_partial_trajectories(
    y: np.ndarray,
    sr: int,
    start_time: float,
    end_time: float,
    n_peaks: int = 15,
    fmin: float = 50.0,
    fmax: float = 5000.0,
    n_fft: int = 1024,
    hop_length: int = 256,
    threshold_ratio: float = 0.15,
) -> list[dict]:
    """
    Track each spectral peak (partial) individually across time and report
    when it onsets, when it peaks, and when it decays away -- rather than
    treating all peaks as if they coexist at one single peak_time.

    This matters for percussive/concrete material where a bright transient
    (e.g. a noisy attack) can be strongest in the first ~50ms and gone
    within 200ms, while the fundamental persists through the whole decay --
    a single overall peak_time can't represent that.

    Candidate partials are found from the *envelope* of each frequency
    bin (its max magnitude anywhere in [start_time, end_time]), not just
    magnitude at one instant, so short-lived attack-only partials aren't
    missed. Each partial then gets its own onset/peak/offset relative to
    its own maximum (threshold_ratio), and a representative reassigned
    frequency averaged over the frames where it's actually active.

    Returns a list of dicts sorted by onset_time, each with:
        freq, relative_amp, onset_time, peak_time, offset_time
    """
    freqs_reassigned, _times_reassigned, mags = librosa.reassigned_spectrogram(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length, fill_nan=True)
    bin_freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    frame_times = librosa.frames_to_time(np.arange(mags.shape[1]), sr=sr, hop_length=hop_length)

    frame_mask = (frame_times >= start_time) & (frame_times <= end_time)
    frame_indices = np.where(frame_mask)[0]
    if len(frame_indices) == 0:
        return []

    mags_range = mags[:, frame_indices]
    freqs_range = freqs_reassigned[:, frame_indices]
    times_range = frame_times[frame_indices]

    freq_mask = (bin_freqs >= fmin) & (bin_freqs <= fmax)
    bin_indices = np.where(freq_mask)[0]

    # Envelope per bin = its loudest moment anywhere in range, so a partial
    # that's only strong during the attack still gets picked as a candidate.
    bin_envelope = mags_range[bin_indices, :].max(axis=1)

    if bin_envelope.max() <= 0:
        return []

    peak_local_idx, _ = find_peaks(
        bin_envelope,
        prominence=bin_envelope.max() * 0.03,
        distance=2,
    )
    candidate_bins = bin_indices[peak_local_idx]

    candidate_envelope = bin_envelope[peak_local_idx]
    order = np.argsort(candidate_envelope)[::-1][:n_peaks]
    candidate_bins = candidate_bins[order]

    overall_max = candidate_envelope[order].max()

    results = []
    for idx in candidate_bins:
        mag_series = mags_range[idx, :]
        freq_series = freqs_range[idx, :]
        own_max = mag_series.max()
        if own_max <= 0:
            continue
        active = mag_series >= (own_max * threshold_ratio)
        active_indices = np.where(active)[0]
        if len(active_indices) == 0:
            continue

        onset_i, offset_i = active_indices[0], active_indices[-1]
        peak_i = int(np.argmax(mag_series))

        valid_freqs = freq_series[active_indices]
        valid_freqs = valid_freqs[(valid_freqs > 0) & np.isfinite(valid_freqs)]
        representative_freq = float(np.median(valid_freqs)) if len(valid_freqs) > 0 else float(bin_freqs[idx])

        results.append({
            "freq": round(representative_freq, 1),
            "relative_amp": round(float(own_max / overall_max), 3),
            "onset_time": round(float(times_range[onset_i]), 3),
            "peak_time": round(float(times_range[peak_i]), 3),
            "offset_time": round(float(times_range[offset_i]), 3),
        })

    results.sort(key=lambda r: r["onset_time"])
    return results


def analyze_sound(file_path: str, n_peaks: int = 15, fmin: float = 50.0, fmax: float = 5000.0) -> dict:
    """
    Returns (sound_data, trajectories) -- sound_data is the SoundData-shaped
    summary (fundamental/first_partial/peaks/timing), trajectories is the
    full per-partial onset/peak/offset list it was derived from.
    """
    y, sr = librosa.load(file_path, sr=None, mono=True)
    timing = analyze_timing(y, sr)
    trajectories = analyze_partial_trajectories(
        y, sr, start_time=timing["start_time"], end_time=timing["end_time"], n_peaks=n_peaks, fmin=fmin, fmax=fmax
    )
    result = {k: v for k, v in timing.items() if not k.startswith("_")}
    result.update(summarize_partials(trajectories))
    result["trajectories"] = trajectories

    return result


SPECTRUM_SIZE = 50


@dataclass
class SoundPartial:
    frequency: float
    onset_time: float = 0.0
    peak_time: float = 0.0
    offset_time: float = 0.0
    amplitude: float = 0.0


@dataclass
class SoundData:
    sound: StrEnum
    file_name: str
    duration: float
    fundamental: SoundPartial
    first_partial: SoundPartial
    start_time: float
    end_time: float
    peak_time: float
    partials: list[SoundPartial] = field(default_factory=list)

    def make_fact(self) -> float:
        return make_fact(fundamental=self.fundamental.frequency, first_partial=self.first_partial.frequency)

    def make_spectrum(self) -> list[float]:
        fact = self.make_fact()
        return make_spectrum(fundamental=self.fundamental.frequency, fact=fact, size=SPECTRUM_SIZE)

    def make_undertone_spectrum(self) -> list[float]:
        fact = self.make_fact()
        return make_undertone_spectrum(fundamental=self.fundamental.frequency, fact=fact, size=SPECTRUM_SIZE)

    def get_relative_peak_time(self, reverse: bool = False) -> tuple[float, float]:
        relative_peak_time = (self.peak_time - self.start_time) / (self.end_time - self.start_time)
        if reverse:
            relative_peak_time = 1.0 - relative_peak_time
        relative_times = (relative_peak_time, 1.0 - relative_peak_time)

        return relative_times

    def get_relative_start_end(self) -> tuple[float, float]:
        return (self.start_time / self.duration, self.end_time / self.duration)

    def make_rate(self, second_freq: float) -> float:
        return second_freq / self.fundamental.frequency

    def add_sound_to_synth_player(self, synth_player: SynthPlayerV2):
        synth_player.add_sound(self.sound, self.file_name, self.start_time, self.end_time)

    def get_play_duration(self, rate: float) -> float:
        return (self.end_time - self.start_time) * rate

    @classmethod
    def from_analysis(cls, sound: StrEnum, file_name: str) -> "SoundData":
        analysis = analyze_sound(file_name)
        trajectories = analysis["trajectories"]
        partials = [
            SoundPartial(
                frequency=t["freq"],
                onset_time=t["onset_time"],
                peak_time=t["peak_time"],
                offset_time=t["offset_time"],
                amplitude=t["relative_amp"],
            )
            for t in trajectories
        ]
        by_amp = sorted(partials, key=lambda p: p.amplitude, reverse=True)
        fundamental = by_amp[0] if by_amp else SoundPartial(frequency=0.0)
        first_partial = by_amp[1] if len(by_amp) > 1 else fundamental

        return cls(
            sound=sound,
            file_name=file_name,
            duration=analysis["duration"],
            fundamental=fundamental,
            first_partial=first_partial,
            start_time=analysis["start_time"],
            end_time=analysis["end_time"],
            peak_time=analysis["peak_time"],
            partials=partials,
        )
