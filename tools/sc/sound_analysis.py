"""
sound_analysis.py

Analyzes a sound file to extract timing (start_time, end_time, peak_time)
and spectral peak data (fundamental, first_partial, full peak list), in
the shape expected by the SoundData dataclass in concrete_music_15.

This is meant as a first-pass automated analysis to compare against your
manual Sonic Visualiser / Audacity readings, not to replace judgement on
ambiguous or borderline sounds.

Usage:
    uv run python sound_analysis.py path/to/H1.aif
    uv run python sound_analysis.py path/to/H1.aif --name H1 --n-peaks 12

Requires: librosa, scipy, numpy, soundfile (pip install librosa scipy numpy soundfile)
"""

import argparse
import warnings

import librosa
import numpy as np
from scipy.signal import find_peaks

# librosa's reassigned_spectrogram internally calls np.less(..., where=...)
# without out=, which triggers a harmless UserWarning about uninitialized
# memory in masked-out positions. It doesn't affect the values we actually
# use (validated against known synthetic frequencies), so it's suppressed
# here rather than left to clutter notebook output on every call.
warnings.filterwarnings(
    "ignore",
    message="'where' used without 'out'",
    category=UserWarning,
)


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


def print_partial_trajectories(trajectories: list[dict]) -> None:
    print("# Partial trajectories (freq, relative_amp, onset -> peak -> offset):")
    for p in trajectories:
        print(f"#   {p['freq']:>8.1f} Hz  amp={p['relative_amp']:.3f}  {p['onset_time']:.3f}s -> {p['peak_time']:.3f}s -> {p['offset_time']:.3f}s")


def analyze_sound(file_path: str, n_peaks: int = 15, fmin: float = 50.0, fmax: float = 5000.0) -> tuple[dict, list[dict]]:
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
    return result, trajectories


def print_sound_data_snippet(name: str, file_name: str, data: dict) -> None:
    print(f"Sounds.{name}: SoundData(")
    print(f"    sound=Sounds.{name},")
    print(f'    file_name=f"{{SOUNDPATH}}/{file_name}",')
    print(f"    duration={data['duration']},")
    print(f"    fundamental={data['fundamental']},")
    print(f"    first_partial={data['first_partial']},")
    print(f"    start_time={data['start_time']},")
    print(f"    end_time={data['end_time']},")
    print(f"    peak_time={data['peak_time']},")
    print("),")
    print(f"# Full peak list ({name}): {data['peaks']}")
    print(f"# Relative amplitudes: {data['peak_amplitudes']}")


def main():
    parser = argparse.ArgumentParser(description="Analyze a sound file for timing and spectral peaks.")
    parser.add_argument("file", help="Path to the sound file (.aif, .wav, etc.)")
    parser.add_argument("--name", default="X1", help="Sound enum name for the generated snippet")
    parser.add_argument("--n-peaks", type=int, default=15, help="Number of spectral peaks to extract")
    parser.add_argument("--fmin", type=float, default=50.0, help="Minimum frequency to consider")
    parser.add_argument("--fmax", type=float, default=5000.0, help="Maximum frequency to consider")
    parser.add_argument("--threshold-db", type=float, default=-40.0, help="RMS threshold (dB below peak) for start/end detection")
    parser.add_argument(
        "--trajectories",
        action="store_true",
        help="Also print per-partial onset/peak/offset timing instead of a single overall peak_time",
    )
    args = parser.parse_args()

    y, sr = librosa.load(args.file, sr=None, mono=True)
    timing = analyze_timing(y, sr, threshold_db=args.threshold_db)
    trajectories = analyze_partial_trajectories(
        y, sr, start_time=timing["start_time"], end_time=timing["end_time"], n_peaks=args.n_peaks, fmin=args.fmin, fmax=args.fmax
    )
    data = {k: v for k, v in timing.items() if not k.startswith("_")}
    data.update(summarize_partials(trajectories))

    print_sound_data_snippet(args.name, args.file, data)

    if args.trajectories:
        print_partial_trajectories(trajectories)


if __name__ == "__main__":
    main()
