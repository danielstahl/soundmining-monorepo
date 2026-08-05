import math
import time
from enum import Enum
from typing import Optional, Type, TypeVar

import ipywidgets as widgets
from ipycanvas import Canvas, hold_canvas
from IPython.display import display

from soundmining_library.generative import MarkovChain, random_range
from soundmining_library.piece import Piece
from soundmining_library.sound_data import SoundData
from soundmining_library.supercollider_receiver import ExtendedNoteHandler
from soundmining_library.ui.sound_data_ui import draw_partials
from soundmining_library.ui.ui_piece_model import UiPiece

PIECE_CANVAS_TRACK_HEIGHT = 100
PIECE_CANVAS_NOTE_SCALE_FACTOR = 5
PIECE_CANVAS_HEIGHT_INDENT = 80
PIECE_CANVAS_TRACK_INSET = 15
UI_FONT = "11px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"

# --- constants, alongside the existing PIECE_CANVAS_* ones ---
SPECTRUM_CANVAS_BAR_WIDTH = 26
SPECTRUM_CANVAS_BAR_GAP = 6
SPECTRUM_CANVAS_HEIGHT = 220
SPECTRUM_CANVAS_TOP_PADDING = 26
SPECTRUM_CANVAS_BOTTOM_PADDING = 40
SPECTRUM_CANVAS_LEFT_PADDING = 12


class UiControls:
    def __init__(self, piece: Piece, note_scale_factor: float = PIECE_CANVAS_NOTE_SCALE_FACTOR) -> None:
        self._piece = piece
        self._elements = []
        self.values = {}
        self._note_scale_factor = note_scale_factor

    def header(self, text: str) -> "UiControls":
        self._elements.append(widgets.Label(text))
        return self

    def stop_button(self) -> "UiControls":
        stop_button = widgets.Button(description="Stop", icon="stop", layout=widgets.Layout(width="120px", height="24px"))
        stop_button.add_class("stop-button")

        def stop(b):
            self._piece.reset()

        stop_button.on_click(stop)
        self._elements.append(stop_button)
        return self

    def float_range(self, name: str, description: str, min: float = -1.0, max: float = 1.0, step: float = 0.01, value=[-0.5, 0.5]) -> "UiControls":
        slider = widgets.FloatRangeSlider(
            value=value,
            min=min,
            max=max,
            step=step,
            description=description,
            continuous_update=True,
            orientation="horizontal",
            readout=True,
            readout_format=".2f",
            layout=widgets.Layout(width="400px"),
            style={"description_width": "initial", "handle_color": "#00ff88"},
        )
        self._elements.append(slider)
        self.values[name] = value

        def on_change(change):
            if change["type"] == "change" and change["name"] == "value":
                self.values[name] = change["new"]

        slider.observe(on_change)
        return self

    def int_range(self, name: str, description: str, min: int = -10, max: int = 10, step: int = 1, value=[-5, 5]) -> "UiControls":
        slider = widgets.IntRangeSlider(
            value=value,
            min=min,
            max=max,
            step=step,
            description=description,
            continuous_update=True,
            orientation="horizontal",
            readout=True,
            readout_format="d",
            layout=widgets.Layout(width="400px"),
            style={"description_width": "initial", "handle_color": "#00ff88"},
        )
        self._elements.append(slider)
        self.values[name] = value

        def on_change(change):
            if change["type"] == "change" and change["name"] == "value":
                self.values[name] = change["new"]

        slider.observe(on_change)
        return self

    T = TypeVar("T", bound=Enum)

    def enum_chooose(self, name: str, the_enum: Type[T], default: Optional[T] = None) -> "UiControls":
        options = [e.value for e in the_enum]
        current_value = default.value if default is not None else list(the_enum)[0].value

        chooser = widgets.ToggleButtons(options=options, value=current_value, layout=widgets.Layout(width="auto"))
        chooser.add_class("studio-toggle")

        self.values[name] = the_enum(current_value)

        def on_change(change):
            if change["type"] == "change" and change["name"] == "value":
                self.values[name] = the_enum(change["new"])

        chooser.observe(on_change)

        self._elements.append(chooser)
        return self

    def markov_chain_status(self, markov_chain: MarkovChain) -> "UiControls":
        bars = {}
        for prop in markov_chain.proportions():
            bar = widgets.FloatProgress(value=0, min=0, max=1, description=str(prop))
            label = widgets.Label(value="0.0%")
            bar.add_class("studio-progress")
            bars[prop] = (bar, label)

        def update_bars():
            props = markov_chain.proportions()
            for state, (bar, label) in bars.items():
                bar_value = props.get(state, 0.0)
                bar.value = bar_value
                label.value = f"{bar_value:.1%}"

        markov_chain.subscribe(update_bars)

        container = widgets.VBox(tuple(widgets.HBox((bar, label)) for bar, label in bars.values()))

        self._elements.append(container)
        return self

    def sound_grid(self):
        piece = self._piece
        static_control = piece.instruments.static_control
        sounds = piece.synth_player.sound_plays
        grid = widgets.GridspecLayout(len(sounds), 2, layout=widgets.Layout(grid_gap="10px", width="350px"))
        for i, (name, sound_play) in enumerate(sounds.items()):
            label = widgets.Label(value=name.upper())
            label.add_class("widget-label")
            label.layout.display = "flex"
            label.layout.justify_content = "flex-end"
            label.layout.padding = "0px 10px 0px 0px"

            button = widgets.Button(description="Play", icon="play", layout=widgets.Layout(width="60px", height="20px"))
            button.add_class("play-button")  # Uses your green border style

            def on_click(b, n=name):
                elapsed_since_start = time.monotonic() - piece.supercollider_client.mono_start
                start_time = elapsed_since_start - ExtendedNoteHandler.MIDI_DELAY_TIME
                (piece.synth_player.note().sound_mono(n, 1.0, static_control(1.0)).pan(static_control(random_range(-0.25, 0.25))).play(start_time))

            button.on_click(on_click)

            grid[i, 0] = label
            grid[i, 1] = button
        self._elements.append(grid)
        return self

    def divider(self) -> "UiControls":
        self._elements.append(widgets.HTML("<div style='border-bottom: 1px solid #333; width: 100%; margin: 10px 0;'></div>"))
        return self

    def header_label(self, title: str) -> "UiControls":
        self._elements.append(widgets.Label(title))
        return self

    def _get_canvas_width(self, piece_duration: float) -> float:
        return 200 + (piece_duration * self._note_scale_factor)

    def _get_canvas_height(self, nr_of_tracks: int) -> float:
        return PIECE_CANVAS_TRACK_HEIGHT * nr_of_tracks + PIECE_CANVAS_HEIGHT_INDENT

    def piece_canvas(self) -> "UiControls":
        ui_width = self._get_canvas_width(piece_duration=10)
        ui_height = self._get_canvas_height(nr_of_tracks=2)

        self._piece_canvas = Canvas(width=ui_width, height=ui_height)
        self._piece_canvas.layout.width = "100%"
        self._piece_canvas.layout.height = f"{ui_height}px"

        self._canvas_container = widgets.VBox(
            [self._piece_canvas],
            layout=widgets.Layout(
                border="1px solid dimgrey",
                margin="10px 0",
                width="100%",
                overflow="hidden",  # Keeps the "V" shapes from bleeding out
            ),
        )

        self._elements.append(self._canvas_container)

        return self

    def draw_piece(self, ui_piece: UiPiece):
        if not hasattr(self, "_piece_canvas"):
            return
        piece_canvas: Canvas = self._piece_canvas

        # 1. Get Metadata
        duration = ui_piece.get_duration()
        piece_start = ui_piece.get_start()
        all_pitches = [n.freq or n.note for tr in ui_piece.tracks for n in tr.notes]
        min_f = min(all_pitches) if all_pitches else 0
        max_f = max(all_pitches) if all_pitches else 100
        f_range = (max_f - min_f) or 1.0

        # 2. Calculate Dimensions
        ui_width = 200 + (duration * self._note_scale_factor)
        ui_height = PIECE_CANVAS_TRACK_HEIGHT * len(ui_piece.tracks)

        # 3. ONLY resize if needed (Setting .width clears the canvas!)
        if piece_canvas.width != int(ui_width):
            piece_canvas.width = int(ui_width)
            piece_canvas.layout.width = f"{int(ui_width)}px"
            self._canvas_container.layout.width = f"{int(ui_width)}px"  # key fix
        if piece_canvas.height != int(ui_height):
            piece_canvas.height = int(ui_height)
            piece_canvas.layout.height = f"{int(ui_height)}px"
            self._canvas_container.layout.height = f"{int(ui_height)}px"  # key fix

        # 4. Correctly wrap the canvas instance
        with hold_canvas(piece_canvas):
            piece_canvas.clear()

            # Darken background slightly so white/colors pop
            piece_canvas.fill_style = "#1a1a1a"
            piece_canvas.fill_rect(0, 0, piece_canvas.width, piece_canvas.height)

            piece_canvas.fill_style = "White"
            piece_canvas.font = UI_FONT
            piece_canvas.text_baseline = "middle"  # Keeps the text perfectly centered vertically
            piece_canvas.text_align = "left"

            for idx, track in enumerate(sorted(ui_piece.tracks, key=lambda tr: tr.track_name)):
                # 1. Define lane boundaries
                lane_top = idx * PIECE_CANVAS_TRACK_HEIGHT
                lane_bottom = (idx + 1) * PIECE_CANVAS_TRACK_HEIGHT
                # lane_height = PIECE_CANVAS_TRACK_HEIGHT

                # 2. Define the "Safe Zone" (The area where notes actually live)
                safe_top = lane_top + PIECE_CANVAS_TRACK_INSET
                safe_bottom = lane_bottom - PIECE_CANVAS_TRACK_INSET
                safe_height = safe_bottom - safe_top

                # Draw a bottom border for the track lane
                piece_canvas.stroke_style = "#333333"  # A subtle dark grey
                piece_canvas.line_width = 1
                y_divider = (idx + 1) * PIECE_CANVAS_TRACK_HEIGHT
                piece_canvas.stroke_lines([(0, y_divider), (piece_canvas.width, y_divider)])

                # 2. Draw Track Label (using the center)
                y_center = lane_top + (PIECE_CANVAS_TRACK_HEIGHT / 2)
                piece_canvas.fill_text(track.track_name, 20, y_center)

                for note in track.notes:
                    # Proper Pitch Math
                    pitch = note.freq or note.note
                    rel_f = (pitch - min_f) / f_range

                    # X Math (Start at 200)
                    sx = 200 + ((note.start - piece_start) * self._note_scale_factor)
                    px = sx + (note.duration * note.peak * self._note_scale_factor)
                    ex = sx + (note.duration * self._note_scale_factor)

                    # Y Math (Offset by 10 to prevent clipping)
                    # We draw UP from the floor
                    sy = safe_bottom - (rel_f * safe_height)
                    py = sy - 8  # Peak

                    piece_canvas.stroke_style = note.color
                    piece_canvas.line_width = 2
                    piece_canvas.stroke_lines([(sx, sy), (px, py), (ex, sy)])

    # PARTIAL_CANVAS_HEIGHT = 400
    PARTIAL_CANVAS_HEIGHT = 600
    # PARTIAL_CANVAS_TIME_SCALE_FACTOR = 400  # pixels per second
    PARTIAL_CANVAS_TIME_SCALE_FACTOR = 600  # pixels per second

    def _get_partial_canvas_width(self, duration: float) -> float:
        return 200 + (duration * self.PARTIAL_CANVAS_TIME_SCALE_FACTOR)

    def partial_canvas(self, sound_data: SoundData) -> "UiControls":
        static_control = self._piece.instruments.static_control

        ui_width = int(self._get_partial_canvas_width(duration=sound_data.duration))
        ui_height = self.PARTIAL_CANVAS_HEIGHT

        canvas = Canvas(width=ui_width, height=ui_height)
        canvas.layout.width = f"{ui_width}px"  # was "100%" -- pin to native resolution so text renders 1:1, not browser-stretched
        canvas.layout.height = f"{ui_height}px"
        draw_partials(sound_data, canvas, width=ui_width, height=ui_height)

        play_button = widgets.Button(description="Play", icon="play", layout=widgets.Layout(width="60px", height="20px"))
        play_button.add_class("play-button")

        def on_click(b, sound_name=sound_data.sound):
            elapsed_since_start = time.monotonic() - self._piece.supercollider_client.mono_start
            start_time = elapsed_since_start - ExtendedNoteHandler.MIDI_DELAY_TIME
            (
                self._piece.synth_player
                .note()
                .sound_mono(sound_name, 1.0, static_control(1.0))
                .pan(static_control(random_range(-0.25, 0.25)))
                .play(start_time)
            )

        play_button.on_click(on_click)

        header = widgets.HBox(
            [widgets.Label(value=str(sound_data.sound).upper()), play_button],
            layout=widgets.Layout(justify_content="space-between", align_items="center"),
        )

        canvas_container = widgets.VBox(
            [header, canvas],
            layout=widgets.Layout(
                border="1px solid dimgrey",
                margin="10px 0",
                width="100%",
                overflow="auto",  # was "hidden" -- a wide/long sound can now scroll instead of silently clipping
            ),
        )
        self._elements.append(canvas_container)
        return self

    def spectrum_canvas(
        self,
        spectrum: list[float],
        title: str = "Spectrum",
        use_log_scale: bool = True,
    ) -> "UiControls":
        if not spectrum:
            return self

        bar_width = SPECTRUM_CANVAS_BAR_WIDTH
        gap = SPECTRUM_CANVAS_BAR_GAP
        n = len(spectrum)
        canvas_width = SPECTRUM_CANVAS_LEFT_PADDING * 2 + n * (bar_width + gap)

        # Reserve a fixed label band sized off the min/max frequency's
        # digit count, since that's what actually drives label length
        # regardless of how many partials sit in between.
        lowest_freq, highest_freq = min(spectrum), max(spectrum)
        max_label_len = max(len(f"{lowest_freq:.0f}"), len(f"{highest_freq:.0f}"))
        approx_char_px = 7  # conservative width per char at 11px font, rotated
        label_band_height = max_label_len * approx_char_px + 10
        title_height = 22
        top_padding = title_height + label_band_height
        canvas_height = top_padding + (SPECTRUM_CANVAS_HEIGHT - SPECTRUM_CANVAS_TOP_PADDING) + SPECTRUM_CANVAS_BOTTOM_PADDING - title_height

        canvas = Canvas(width=canvas_width, height=canvas_height)
        canvas.layout.width = f"{canvas_width}px"
        canvas.layout.height = f"{canvas_height}px"

        plot_top = top_padding
        plot_bottom = canvas_height - SPECTRUM_CANVAS_BOTTOM_PADDING
        plot_height = plot_bottom - plot_top
        label_anchor_y = plot_top - 8

        def scaled(value: float) -> float:
            return math.log10(max(value, 1e-6)) if use_log_scale else value

        values = [scaled(v) for v in spectrum]
        min_v, max_v = min(values), max(values)
        v_range = (max_v - min_v) or 1.0

        with hold_canvas(canvas):
            canvas.fill_style = "#1a1a1a"
            canvas.fill_rect(0, 0, canvas_width, canvas_height)

            canvas.fill_style = "White"
            canvas.font = UI_FONT
            canvas.text_align = "center"
            canvas.text_baseline = "bottom"
            canvas.fill_text(title, canvas_width / 2, 16)

            canvas.stroke_style = "#333333"
            canvas.line_width = 1
            canvas.stroke_lines([(0, plot_bottom), (canvas_width, plot_bottom)])

            for i, (freq, val) in enumerate(zip(spectrum, values)):
                x = SPECTRUM_CANVAS_LEFT_PADDING + i * (bar_width + gap)
                rel = (val - min_v) / v_range
                bar_height = max(rel * plot_height, 2)
                y = plot_bottom - bar_height

                canvas.fill_style = "#00d1ff"
                canvas.fill_rect(x, y, bar_width, bar_height)

                canvas.save()
                canvas.translate(x + bar_width / 2, label_anchor_y)
                canvas.rotate(-math.pi / 2)
                canvas.text_align = "left"
                canvas.text_baseline = "middle"
                canvas.fill_style = "White"
                canvas.font = UI_FONT
                canvas.fill_text(f"{freq:.1f}", 0, 0)
                canvas.restore()

                canvas.stroke_style = "#444444"
                canvas.line_width = 1
                canvas.stroke_lines([(x + bar_width / 2, plot_top - 2), (x + bar_width / 2, y)])

                canvas.text_align = "center"
                canvas.text_baseline = "top"
                canvas.fill_style = "#888888"
                canvas.fill_text(str(i), x + bar_width / 2, plot_bottom + 4)

        canvas_container = widgets.Box(
            [canvas],
            layout=widgets.Layout(
                border="1px solid dimgrey",
                margin="10px 0",
                width="100%",
                overflow_x="auto",
            ),
        )

        listing_html = (
            '<div style=\'font-family: "Courier New", monospace; font-size: 11px; '
            "color: whitesmoke; padding: 4px 2px; word-break: break-word;'>" + ", ".join(f"[{i}] {v:.2f}" for i, v in enumerate(spectrum)) + "</div>"
        )

        self._elements.append(canvas_container)
        self._elements.append(widgets.HTML(listing_html))
        return self

    def _output_style(self):
        style_html = """
            <style>
                :root {
                    --text-color: whitesmoke
                }
                /* description text */
                .widget-label {
                    color: var(--text-color) !important;
                    font-size: 11px !important;
                    text-shadow: 0 0 5px rgba(0, 209, 255, 0.5) !important;
                    height: 22px !important;
                    line-height: 22px !important;        
                }    
                
                /* the numbers next to the slider */
                .widget-readout {
                    color: var(--text-color) !important;
                    font-family: 'Courier New', monospace !important;
                    font-size: 14px !important;
                }

                /* Style the slider track itself */
                .noUi-connect {
                    background: #00ff88 !important;
                }

                .studio-box {
                    background-color: #1e1e1e !important;
                    border: 1px solid #444444 !important; /* Slightly darker grey for the main box */
                    border-radius: 6px;        
                }
                .play-button, .stop-button {
                    background-color: transparent !important;
                    height: 22px !important;
                    line-height: 20px !important;
                    font-size: 10px !important;
                    border: 1px solid #666666 !important; /* Middle Grey */
                    border-radius: 2px !important;
                    transition: all 0.2s ease-in-out !important;
                    margin: 2px !important;
                }
                .play-button { color: var(--text-color) !important; }
                .play-button i { color: springgreen !important; }
                .play-button:hover {
                    border-color: springgreen !important;
                    background-color: rgba(0, 255, 136, 0.1) !important;
                }
                .stop-button { 
                    color: var(--text-color) !important; 
                    margin-top: 15px !important; /* Give it some space from the list */
                }
                .stop-button i { color: tomato !important; }
                .stop-button:hover {
                    border-color: tomato !important;
                    background-color: rgba(255, 68, 68, 0.1) !important;
                }

                /* The Main Container */
                .studio-box {
                    background-color: #1e1e1e !important;
                    border: 1px solid #444444 !important;
                    border-radius: 6px;
                }
                .sound-row {
                    margin-bottom: 5px;
                    padding: 5px;
                    border-bottom: 1px solid #333;
                }
                
                .studio-toggle .jupyter-button {
                    background-color: #1e1e1e; /* Removed !important here */
                    border: 1px solid #444444 !important;
                    color: var(--text-color) !important;
                    padding: 2px 8px !important; 
                    font-size: 10px !important;
                    line-height: 1 !important;
                    min-width: 30px !important;
                    height: 22px !important;
                }
                
                .studio-toggle .jupyter-button.mod-active,
                .studio-toggle input:checked + .jupyter-button {
                    background-color: #1e1e1e !important; /* Only use !important here */
                    color: var(--text-color) !important;
                    border-color: springgreen !important;
                }
                 
                .studio-toggle {
                    gap: 2px !important;
                }
                
                .studio-toggle .jupyter-button:focus,
                .studio-toggle .jupyter-button:focus-visible {
                    outline: none !important;
                    box-shadow: none !important;
                }

                /* Progress bar track */
                .studio-progress .progress {
                    height: 8px !important;
                    background-color: #1e1e1e !important;
                    border: 1px solid #444444 !important;
                }

                /* Progress bar fill */
                .studio-progress .progress-bar {
                    background-color: springgreen !important;
                }

                /* Description label */
                .studio-progress .widget-label {
                    color: var(--text-color) !important;
                    font-size: 10px !important;
                    min-width: 60px !important;
                }

            </style>
            """
        display(widgets.HTML(style_html))

    def _widget(self, widget: widgets.Widget) -> "UiControls":
        self._elements.append(widget)
        return self

    def render(self) -> "UiControls":
        self._output_style()
        ui = widgets.VBox(
            self._elements,
            layout=widgets.Layout(
                display="flex",
                flex_flow="column",
                align_items="stretch",
                width="100%",
                # max_width="1000px",
                # min_width="300px",
                overflow="visible",
                padding="10px",
                border="1px solid #444",
                background_color="#1e1e1e",
            ),
        )
        ui.add_class("studio-box")
        display(ui)
        return self
