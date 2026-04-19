import time

import ipywidgets as widgets
from ipycanvas import Canvas, hold_canvas
from IPython.display import display

from soundmining_library.generative import random_range
from soundmining_library.piece import Piece
from soundmining_library.supercollider_receiver import ExtendedNoteHandler
from soundmining_library.ui.ui_piece_model import UiPiece

PIECE_CANVAS_TRACK_HEIGHT = 100
PIECE_CANVAS_NOTE_SCALE_FACTOR = 5
PIECE_CANVAS_HEIGHT_INDENT = 80
PIECE_CANVAS_TRACK_INSET = 15
UI_FONT = "11px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"


class UiControls:
    def __init__(self, piece: Piece) -> None:
        self._piece = piece
        self._elements = []
        self.float_range_sliders = {}

    def header(self, text: str) -> "UiControls":
        self._elements.append(widgets.Label("text"))
        return self

    def stop_button(self) -> "UiControls":
        stop_button = widgets.Button(description="Stop", icon="stop", layout=widgets.Layout(width="120px", height="24px"))
        stop_button.add_class("stop-button")

        def stop(b):
            self._piece.reset()

        stop_button.on_click(stop)
        self._elements.append(stop_button)
        return self

    def range_floatslider(
        self, name: str, description: str, min: float = -1.0, max: float = 1.0, step: float = 0.01, value=[-0.5, 0.5]
    ) -> "UiControls":
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
        self.float_range_sliders[name] = slider
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
        return 200 + (piece_duration * PIECE_CANVAS_NOTE_SCALE_FACTOR)

    def _get_canvas_height(self, nr_of_tracks: int) -> float:
        return PIECE_CANVAS_TRACK_HEIGHT * nr_of_tracks + PIECE_CANVAS_HEIGHT_INDENT

    def piece_canvas(self) -> "UiControls":
        ui_width = self._get_canvas_width(piece_duration=10)
        ui_height = self._get_canvas_height(nr_of_tracks=2)

        self._piece_canvas = Canvas(width=ui_width, height=ui_height)
        self._piece_canvas.layout.width = "100%"
        self._piece_canvas.layout.height = f"{ui_height}px"

        canvas_container = widgets.VBox(
            [self._piece_canvas],
            layout=widgets.Layout(
                border="1px solid dimgrey",
                margin="10px 0",
                width="100%",
                overflow="hidden",  # Keeps the "V" shapes from bleeding out
            ),
        )

        self._elements.append(canvas_container)

        return self

    def draw_piece(self, ui_piece: UiPiece):
        if not hasattr(self, "_piece_canvas"):
            return
        piece_canvas: Canvas = self._piece_canvas

        # 1. Get Metadata
        duration = ui_piece.get_duration() or 1.0
        all_pitches = [n.freq or n.note for tr in ui_piece.tracks for n in tr.notes]
        min_f = min(all_pitches) if all_pitches else 0
        max_f = max(all_pitches) if all_pitches else 100
        f_range = (max_f - min_f) or 1.0

        # 2. Calculate Dimensions
        ui_width = 200 + (duration * PIECE_CANVAS_NOTE_SCALE_FACTOR)
        ui_height = PIECE_CANVAS_TRACK_HEIGHT * len(ui_piece.tracks)

        # 3. ONLY resize if needed (Setting .width clears the canvas!)
        if piece_canvas.width != int(ui_width):
            piece_canvas.width = int(ui_width)
            piece_canvas.layout.width = f"{int(ui_width)}px"
        if piece_canvas.height != int(ui_height):
            piece_canvas.height = int(ui_height)
            piece_canvas.layout.height = f"{int(ui_height)}px"

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
                    sx = 200 + (note.start * PIECE_CANVAS_NOTE_SCALE_FACTOR)
                    px = sx + (note.duration * note.peak * PIECE_CANVAS_NOTE_SCALE_FACTOR)
                    ex = sx + (note.duration * PIECE_CANVAS_NOTE_SCALE_FACTOR)

                    # Y Math (Offset by 10 to prevent clipping)
                    # We draw UP from the floor
                    sy = safe_bottom - (rel_f * safe_height)
                    py = sy - 8  # Peak

                    piece_canvas.stroke_style = note.color
                    piece_canvas.line_width = 2
                    piece_canvas.stroke_lines([(sx, sy), (px, py), (ex, sy)])

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
                
            </style>
            """
        display(widgets.HTML(style_html))

    def render(self) -> "UiControls":
        self._output_style()
        ui = widgets.VBox(
            self._elements,
            layout=widgets.Layout(
                display="flex",
                flex_flow="column",
                align_items="stretch",
                width="100%",
                max_width="1000px",
                min_width="300px",
                padding="10px",
                border="1px solid #444",
                background_color="#1e1e1e",
            ),
        )
        ui.add_class("studio-box")
        display(ui)
        return self
