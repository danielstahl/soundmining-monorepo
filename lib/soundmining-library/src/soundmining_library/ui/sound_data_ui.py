import math

from ipycanvas import Canvas, hold_canvas

from soundmining_library.sound_data import SoundData

CANVAS_WIDTH = 900
CANVAS_HEIGHT = 400
LEFT_MARGIN = 90
RIGHT_MARGIN = 20
TOP_MARGIN = 40
BOTTOM_MARGIN = 50
TIME_MARGIN_RATIO = 0.05

COLOR_FUNDAMENTAL = "#00ff88"
COLOR_FIRST_PARTIAL = "#ffaa33"
COLOR_PARTIAL = "#8899aa"
COLOR_BG = "#1a1a1a"
COLOR_GRID = "#333333"
COLOR_TEXT = "whitesmoke"

UI_FONT = "11px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"


def _freq_to_y(freq: float, min_freq: float, max_freq: float, plot_top: float, plot_bottom: float) -> float:
    """Log-scale frequency axis: keeps low and high partials from being
    squashed together the way a linear axis would, and matches how
    frequency is perceived."""
    freq = max(freq, min_freq)
    log_min = math.log2(min_freq)
    log_max = math.log2(max_freq)
    if log_max == log_min:
        return (plot_top + plot_bottom) / 2
    t = (math.log2(freq) - log_min) / (log_max - log_min)
    return plot_bottom - t * (plot_bottom - plot_top)  # higher freq nearer top


def _time_to_x(time: float, min_time: float, max_time: float, plot_left: float, plot_right: float) -> float:
    if max_time == min_time:
        return plot_left
    t = (time - min_time) / (max_time - min_time)
    return plot_left + t * (plot_right - plot_left)


def _amplitude_to_linewidth(amplitude: float, min_width: float = 1.5, max_width: float = 6.0) -> float:
    amplitude = max(0.0, min(1.0, amplitude))
    return min_width + amplitude * (max_width - min_width)


def _nice_frequency_ticks(min_freq: float, max_freq: float, target_count: int = 6) -> list[float]:
    """Roughly `target_count` gridline frequencies, evenly spaced on the
    same log scale the plot itself uses."""
    if min_freq <= 0:
        min_freq = 20.0
    log_min = math.log2(min_freq)
    log_max = math.log2(max_freq)
    steps = max(1, target_count - 1)
    return [2 ** (log_min + (i / steps) * (log_max - log_min)) for i in range(target_count)]


def _draw_legend_item(canvas: Canvas, x: float, y: float, color: str, label: str) -> None:
    canvas.fill_style = color
    canvas.fill_rect(x, y - 5, 10, 10)
    canvas.fill_style = COLOR_TEXT
    canvas.text_align = "left"
    canvas.text_baseline = "middle"
    canvas.font = UI_FONT
    canvas.fill_text(label, x + 16, y)


def draw_partials(sound_data: SoundData, canvas: Canvas, width: int = CANVAS_WIDTH, height: int = CANVAS_HEIGHT) -> None:
    """
    Draw the partial-track view onto an existing Canvas. Split out from
    show_partial_view() so it can be reused inside a larger composite UI
    (e.g. alongside the existing piece_canvas) rather than always creating
    its own standalone widget.
    """
    all_partials = list(sound_data.partials) or [sound_data.fundamental, sound_data.first_partial]
    all_partials = [p for p in all_partials if p is not None and p.frequency > 0]
    if not all_partials:
        raise ValueError("SoundData has no partials with a nonzero frequency to display")

    freqs = [p.frequency for p in all_partials]
    min_freq = min(freqs) * 0.9
    max_freq = max(freqs) * 1.1

    min_time = 0.0
    max_time = sound_data.duration
    time_span = max_time - min_time
    pad = time_span * TIME_MARGIN_RATIO
    plot_min_time = min_time - pad
    plot_max_time = max_time + pad

    plot_left = LEFT_MARGIN
    plot_right = width - RIGHT_MARGIN
    plot_top = TOP_MARGIN
    plot_bottom = height - BOTTOM_MARGIN

    with hold_canvas(canvas):
        canvas.fill_style = COLOR_BG
        canvas.fill_rect(0, 0, width, height)

        # frequency gridlines + labels
        canvas.font = UI_FONT
        for gf in _nice_frequency_ticks(min_freq, max_freq):
            gy = _freq_to_y(gf, min_freq, max_freq, plot_top, plot_bottom)
            canvas.stroke_style = COLOR_GRID
            canvas.line_width = 1
            canvas.stroke_lines([(plot_left, gy), (plot_right, gy)])
            canvas.fill_style = COLOR_TEXT
            canvas.text_align = "right"
            canvas.text_baseline = "middle"
            canvas.fill_text(f"{gf:.0f} Hz", plot_left - 8, gy)

        # time axis ticks
        n_ticks = 6
        for i in range(n_ticks + 1):
            tt = plot_min_time + (i / n_ticks) * (plot_max_time - plot_min_time)
            tx = _time_to_x(tt, plot_min_time, plot_max_time, plot_left, plot_right)
            canvas.stroke_style = COLOR_GRID
            canvas.stroke_lines([(tx, plot_top), (tx, plot_bottom)])
            canvas.fill_style = COLOR_TEXT
            canvas.text_align = "center"
            canvas.text_baseline = "top"
            canvas.fill_text(f"{tt:.2f}s", tx, plot_bottom + 6)

        # partials
        for i, p in enumerate(all_partials):
            is_fundamental = p is sound_data.fundamental
            is_first_partial = (not is_fundamental) and (p is sound_data.first_partial)
            if is_fundamental:
                color = COLOR_FUNDAMENTAL
            elif is_first_partial:
                color = COLOR_FIRST_PARTIAL
            else:
                color = COLOR_PARTIAL

            y = _freq_to_y(p.frequency, min_freq, max_freq, plot_top, plot_bottom)
            x_start = _time_to_x(p.onset_time, plot_min_time, plot_max_time, plot_left, plot_right)
            x_end = _time_to_x(p.offset_time, plot_min_time, plot_max_time, plot_left, plot_right)
            x_peak = _time_to_x(p.peak_time, plot_min_time, plot_max_time, plot_left, plot_right)

            canvas.stroke_style = color
            canvas.line_width = _amplitude_to_linewidth(p.amplitude)
            canvas.stroke_lines([(x_start, y), (x_end, y)])

            # Peak marker radius must scale with this partial's own line
            # width, or a fixed radius gets fully swallowed by thick lines.
            # fundamental is *always* relative_amp=1.0 (everything else is
            # normalized against it), so it always gets the thickest line --
            # a fixed radius equal to half the max line width (the original
            # bug here) renders with zero visible protrusion for exactly the
            # partials most likely to be fundamental/first_partial.
            peak_radius = max(4.0, canvas.line_width / 2 + 2.0)
            canvas.fill_style = color
            canvas.fill_circle(x_peak, y, peak_radius)

            canvas.font = UI_FONT
            canvas.text_align = "left"
            canvas.text_baseline = "middle"
            canvas.fill_text(f"[{i}] {p.frequency:.1f} Hz", x_end + 6, y)

        # legend
        legend_y = plot_top - 20
        _draw_legend_item(canvas, plot_left, legend_y, COLOR_FUNDAMENTAL, "Fundamental")
        _draw_legend_item(canvas, plot_left + 140, legend_y, COLOR_FIRST_PARTIAL, "First partial")
        _draw_legend_item(canvas, plot_left + 300, legend_y, COLOR_PARTIAL, "Partial")
