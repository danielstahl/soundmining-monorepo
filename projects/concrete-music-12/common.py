from enum import StrEnum
from piece import piece
from soundmining_tools.modular import instrument
from soundmining_tools import supercollider_client
from soundmining_tools.modular.instrument import NodeId
from soundmining_tools.generative import MarkovChain, random_int_range, random_range, pan_point
from soundmining_tools.modular.synth_player import SynthNote
from soundmining_tools.sequencer import SequenceNote
import random
import math

SOUND_PATH = (
    "/Users/danielstahl/Documents/Music/Pieces/Concrete Music/Concrete Music 11/sounds/Concrete Music 11_sounds"
)
# IR_PATH = "/Users/danielstahl/Documents/Music/impulse-response/convolution-ir"
IR_PATH = "/Users/danielstahl/Documents/Music/Pieces/Concrete Music/Concrete Music 11/convolution-ir"

SoundType = StrEnum("SoundType", ["LOW", "MIDDLE", "HIGH"])

Sound = StrEnum(
    "Sound",
    [
        "LONG_RATTLE_1",
        "LONG_RATTLE_2",
        "LONG_SCRATCH_1",
        "LONG_SCRATCH_2",
        "MIDDLE_SCRATCH_1",
        "POT_HIT_LONG_1",
        "POT_HIT_LONG_2",
        "POT_HIT_SHORT_1",
        "POT_HIT_SHORT_2",
        "POT_HIT_SHORT_3",
        "POT_HIT_SHORT_4",
        "POT_HIT_SHORT_5",
        "POT_HIT_SHORT_6",
        "POT_HIT_SHORT_7",
        "POT_HIT_SHORT_8",
        "POT_HIT_SHORT_FLAM_1",
        "POT_HIT_SHORT_FLAM_2",
        "POT_HIT_SHORT_FLAM_3",
        "SCRATCH_HIT_1",
        "SHORT_RATTLE_VARIANT_1_1",
        "SHORT_RATTLE_VARIANT_1_2",
        "SHORT_RATTLE_VARIANT_1_3",
        "SHORT_RATTLE_VARIANT_2_1",
        "SHORT_RATTLE_VARIANT_2_2",
        "SHORT_RATTLE_VARIANT_2_3",
        "SHORT_REPEATED_RATTLES_1",
        "SHORT_SCRATCH_1",
    ],
)

SoundGroup = StrEnum(
    "SoundGroup",
    [
        "LONG_RATTLE",
        "LONG_SCRATCH",
        "MIDDLE_SCRATCH",
        "POT_HIT_LONG",
        "POT_HIT_SHORT",
        "POT_HIT_SHORT_FLAM",
        "SCRATCH_HIT",
        "SHORT_RATTLE_VARIANT_1",
        "SHORT_RATTLE_VARIANT_2",
        "SHORT_REPEATED_RATTLES",
        "SHORT_SCRATCH",
    ],
)

sound_groups = {
    SoundGroup.LONG_RATTLE: [Sound.LONG_RATTLE_1, Sound.LONG_RATTLE_2],
    SoundGroup.LONG_SCRATCH: [Sound.LONG_SCRATCH_1, Sound.LONG_SCRATCH_2],
    SoundGroup.MIDDLE_SCRATCH: [Sound.MIDDLE_SCRATCH_1],
    SoundGroup.POT_HIT_LONG: [Sound.POT_HIT_LONG_1, Sound.POT_HIT_LONG_2],
    SoundGroup.POT_HIT_SHORT: [
        Sound.POT_HIT_SHORT_1,
        Sound.POT_HIT_SHORT_2,
        Sound.POT_HIT_SHORT_3,
        Sound.POT_HIT_SHORT_4,
        Sound.POT_HIT_SHORT_5,
        Sound.POT_HIT_SHORT_6,
        Sound.POT_HIT_SHORT_7,
        Sound.POT_HIT_SHORT_8,
    ],
    SoundGroup.POT_HIT_SHORT_FLAM: [Sound.POT_HIT_SHORT_FLAM_1, Sound.POT_HIT_SHORT_FLAM_2, Sound.POT_HIT_SHORT_FLAM_3],
    SoundGroup.SCRATCH_HIT: [Sound.SCRATCH_HIT_1],
    SoundGroup.SHORT_RATTLE_VARIANT_1: [
        Sound.SHORT_RATTLE_VARIANT_1_1,
        Sound.SHORT_RATTLE_VARIANT_1_2,
        Sound.SHORT_RATTLE_VARIANT_1_3,
    ],
    SoundGroup.SHORT_RATTLE_VARIANT_2: [
        Sound.SHORT_RATTLE_VARIANT_2_1,
        Sound.SHORT_RATTLE_VARIANT_2_2,
        Sound.SHORT_RATTLE_VARIANT_2_3,
    ],
    SoundGroup.SHORT_REPEATED_RATTLES: [Sound.SHORT_REPEATED_RATTLES_1],
    SoundGroup.SHORT_SCRATCH: [Sound.SHORT_SCRATCH_1],
}

sounds = {
    Sound.LONG_RATTLE_1: {},
    Sound.LONG_RATTLE_2: {},
    Sound.LONG_SCRATCH_1: {
        SoundType.LOW: [95, 147, 190, 242, 349, 470],
        SoundType.MIDDLE: [650, 708, 727, 844, 893],
        SoundType.HIGH: [
            1002,
            1058,
            1196,
            1308,
            1406,
            1499,
            1640,
            1660,
            1893,
            3111,
            3536,
            3833,
            5911,
            6423,
            7044,
            7343,
            8738,
            10993,
        ],
    },
    Sound.LONG_SCRATCH_2: {
        SoundType.LOW: [56, 102, 145, 163, 214, 231, 361, 425, 491],
        SoundType.MIDDLE: [534, 607, 632, 680, 750, 783, 848],
        SoundType.HIGH: [
            964,
            1081,
            1170,
            1290,
            1430,
            1599,
            1733,
            3096,
            3394,
            3583,
            6026,
            6370,
            6937,
            7289,
            8726,
            10123,
            11018,
        ],
    },
    Sound.MIDDLE_SCRATCH_1: {},
    Sound.POT_HIT_LONG_1: {
        SoundType.LOW: [181, 325],
        SoundType.MIDDLE: [608, 889],
        SoundType.HIGH: [1148, 1360, 1643, 1992, 2507, 2980, 3251, 3679, 4147, 5907, 7173, 9115, 11043],
    },
    Sound.POT_HIT_LONG_2: {
        SoundType.LOW: [62, 160, 187, 327, 399],
        SoundType.MIDDLE: [545, 606, 795],
        SoundType.HIGH: [
            932,
            1098,
            1320,
            1424,
            1637,
            2136,
            2030,
            2978,
            3139,
            4146,
            5079,
            5809,
            6936,
            8645,
            9988,
            11482,
        ],
    },
    Sound.POT_HIT_SHORT_1: {
        SoundType.LOW: [187],
        SoundType.MIDDLE: [564, 768, 866],
        SoundType.HIGH: [936, 1009, 1195, 1290, 1639, 2927, 3115],
    },
    Sound.POT_HIT_SHORT_2: {
        SoundType.LOW: [353],
        SoundType.MIDDLE: [634, 752, 870],
        SoundType.HIGH: [960, 1033, 1120, 1501, 2086, 2461, 3774],
    },
    Sound.POT_HIT_SHORT_3: {
        SoundType.LOW: [140, 352, 492],
        SoundType.MIDDLE: [657, 770, 869],
        SoundType.HIGH: [960, 1032, 1127, 1192, 1312, 1758, 2273, 2485, 3939, 5015],
    },
    Sound.POT_HIT_SHORT_4: {
        SoundType.LOW: [95, 117, 163, 257],
        SoundType.MIDDLE: [421, 491, 750, 843],
        SoundType.HIGH: [913, 1055, 1219, 1617, 2180, 2508, 3140, 3819, 5414],
    },
    Sound.POT_HIT_SHORT_5: {
        SoundType.LOW: [140, 352, 492],
        SoundType.MIDDLE: [770, 867],
        SoundType.HIGH: [960, 1032, 1192, 1265, 1312, 1758, 2273, 2485, 3029, 3820],
    },
    Sound.POT_HIT_SHORT_6: {
        SoundType.LOW: [92, 140, 213, 328],
        SoundType.MIDDLE: [702, 822],
        SoundType.HIGH: [913, 1054, 1265, 1523, 2297, 3421, 3796, 5976],
    },
    Sound.POT_HIT_SHORT_7: {
        SoundType.LOW: [117, 212, 305, 446],
        SoundType.MIDDLE: [588, 702, 821],
        SoundType.HIGH: [1126, 1622, 2019, 2671, 3797, 4008, 5814, 6422, 10406],
    },
    Sound.POT_HIT_SHORT_8: {
        SoundType.LOW: [74, 132, 218, 347],
        SoundType.MIDDLE: [606, 685, 749, 821],
        SoundType.HIGH: [953, 1076, 1241, 1733, 2884, 3775, 5578, 6304, 9911],
    },
    Sound.POT_HIT_SHORT_FLAM_1: {},
    Sound.POT_HIT_SHORT_FLAM_2: {},
    Sound.POT_HIT_SHORT_FLAM_3: {},
    Sound.SCRATCH_HIT_1: {},
    Sound.SHORT_RATTLE_VARIANT_1_1: {
        SoundType.LOW: [256, 374, 427],
        SoundType.MIDDLE: [688, 843],
        SoundType.HIGH: [960, 1150, 2162, 2285, 2770, 3587, 5070, 6447, 7716, 8594, 9394, 10785, 11416, 13795],
    },
    Sound.SHORT_RATTLE_VARIANT_1_2: {
        SoundType.LOW: [379, 451, 506],
        SoundType.MIDDLE: [703],
        SoundType.HIGH: [1080, 1757, 2595, 3769, 4806, 5113, 5790, 6610, 7172, 8579, 9798, 10991, 11483, 12774],
    },
    Sound.SHORT_RATTLE_VARIANT_1_3: {
        SoundType.LOW: [312, 365, 375, 492],
        SoundType.MIDDLE: [667, 838],
        SoundType.HIGH: [1062, 1757, 2629, 5029, 6447, 7217, 8510, 9422, 10473, 11459, 13594],
    },
    Sound.SHORT_RATTLE_VARIANT_2_1: {
        SoundType.LOW: [143, 282, 328, 395, 559],
        SoundType.MIDDLE: [752],
        SoundType.HIGH: [1106, 1661, 2279, 2959, 3851, 5438, 6073, 6376, 7079, 8486, 10596, 12445, 13124, 15945],
    },
    Sound.SHORT_RATTLE_VARIANT_2_2: {
        SoundType.LOW: [83, 106, 262, 326, 475],
        SoundType.MIDDLE: [693],
        SoundType.HIGH: [1034, 1647, 2740, 3826, 5507, 6045, 6479, 7150, 8391, 10637, 12424, 13688],
    },
    Sound.SHORT_RATTLE_VARIANT_2_3: {
        SoundType.LOW: [282, 394],
        SoundType.MIDDLE: [604, 684],
        SoundType.HIGH: [963, 1175, 1754, 2248, 2948, 3941, 5536, 6092, 6586, 8368, 10404, 12401, 14158, 16031],
    },
    Sound.SHORT_REPEATED_RATTLES_1: {},
    Sound.SHORT_SCRATCH_1: {},
}


def setup_piece():
    piece.reset()
    (
        piece.synth_player.add_sound(Sound.LONG_RATTLE_1, f"{SOUND_PATH}/Long Rattle 1.flac", 0.167, 1.445)
        .add_sound(Sound.LONG_RATTLE_2, f"{SOUND_PATH}/Long Rattle 2.flac", 0.089, 1.345)
        .add_sound(Sound.LONG_SCRATCH_1, f"{SOUND_PATH}/Long Scratch 1.flac", 0.081, 0.850)
        .add_sound(Sound.LONG_SCRATCH_2, f"{SOUND_PATH}/Long Scratch 2.flac", 0.024, 0.926)
        .add_sound(Sound.MIDDLE_SCRATCH_1, f"{SOUND_PATH}/Middle Scratch 1.flac", 0.047, 0.558)
        .add_sound(Sound.POT_HIT_LONG_1, f"{SOUND_PATH}/Pot Hit Long 1.flac", 0.006, 1.077)
        .add_sound(Sound.POT_HIT_LONG_2, f"{SOUND_PATH}/Pot Hit Long 2.flac", 0.019, 0.895)
        .add_sound(Sound.POT_HIT_SHORT_1, f"{SOUND_PATH}/Pot Hit Short 1.flac", 0.010, 0.180)
        .add_sound(Sound.POT_HIT_SHORT_2, f"{SOUND_PATH}/Pot Hit Short 2.flac", 0.105, 0.410)
        .add_sound(Sound.POT_HIT_SHORT_3, f"{SOUND_PATH}/Pot Hit Short 3.flac", 0.022, 0.165)
        .add_sound(Sound.POT_HIT_SHORT_4, f"{SOUND_PATH}/Pot Hit Short 4.flac", 0.036, 0.212)
        .add_sound(Sound.POT_HIT_SHORT_5, f"{SOUND_PATH}/Pot Hit Short 5.flac", 0.062, 0.218)
        .add_sound(Sound.POT_HIT_SHORT_6, f"{SOUND_PATH}/Pot Hit Short 6.flac", 0.057, 0.236)
        .add_sound(Sound.POT_HIT_SHORT_7, f"{SOUND_PATH}/Pot Hit Short 7.flac", 0.030, 0.213)
        .add_sound(Sound.POT_HIT_SHORT_8, f"{SOUND_PATH}/Pot Hit Short 8.flac", 0.088, 0.272)
        .add_sound(Sound.POT_HIT_SHORT_FLAM_1, f"{SOUND_PATH}/Pot Hit Short Flam 1.flac", 0.117, 0.383)
        .add_sound(Sound.POT_HIT_SHORT_FLAM_2, f"{SOUND_PATH}/Pot Hit Short Flam 2.flac", 0.150, 0.387)
        .add_sound(Sound.POT_HIT_SHORT_FLAM_3, f"{SOUND_PATH}/Pot Hit Short Flam 3.flac", 0.198, 0.353)
        .add_sound(Sound.SCRATCH_HIT_1, f"{SOUND_PATH}/Scratch Hit 1.flac", 0.015, 0.615)
        .add_sound(Sound.SHORT_RATTLE_VARIANT_1_1, f"{SOUND_PATH}/Short Rattle Variant 1 1.flac", 0.079, 0.453)
        .add_sound(Sound.SHORT_RATTLE_VARIANT_1_2, f"{SOUND_PATH}/Short Rattle Variant 1 2.flac", 0.222, 0.507)
        .add_sound(Sound.SHORT_RATTLE_VARIANT_1_3, f"{SOUND_PATH}/Short Rattle Variant 1 3.flac", 0.206, 0.634)
        .add_sound(Sound.SHORT_RATTLE_VARIANT_2_1, f"{SOUND_PATH}/Short Rattle Variant 2 1.flac", 0.073, 0.485)
        .add_sound(Sound.SHORT_RATTLE_VARIANT_2_2, f"{SOUND_PATH}/Short Rattle Variant 2 2.flac", 0.193, 0.602)
        .add_sound(Sound.SHORT_RATTLE_VARIANT_2_3, f"{SOUND_PATH}/Short Rattle Variant 2 3.flac", 0.152, 0.493)
        .add_sound(Sound.SHORT_REPEATED_RATTLES_1, f"{SOUND_PATH}/Short Repeated Rattles 1.flac", 0.070, 1.377)
        .add_sound(Sound.SHORT_SCRATCH_1, f"{SOUND_PATH}/Short scratch 1.flac", 0.116, 0.368)
        .add_impulse_response("ir1", f"{IR_PATH}/stalbans_b_ortf-L.wav", f"{IR_PATH}/stalbans_b_ortf-R.wav")
        .add_impulse_response(
            "ir2", f"{IR_PATH}/falkland_tennis_court_ortf-L.wav", f"{IR_PATH}/falkland_tennis_court_ortf-R.wav"
        )
        .add_impulse_response("ir3", f"{IR_PATH}/5UnderpassValencia-L.wav", f"{IR_PATH}/5UnderpassValencia-R.wav")
        .add_impulse_response("ir4", f"{IR_PATH}/DrainageTunnel-L.wav", f"{IR_PATH}/DrainageTunnel-R.wav")
        .add_impulse_response("ir5", f"{IR_PATH}/HartwellTavern-L.wav", f"{IR_PATH}/HartwellTavern-R.wav")
        .add_impulse_response("ir6", f"{IR_PATH}/RacquetballCourt-L.wav", f"{IR_PATH}/RacquetballCourt-R.wav")
        .add_impulse_response("ir7", f"{IR_PATH}/stalbans_a_ortf-L.wav", f"{IR_PATH}/stalbans_a_ortf-R.wav")
        .add_impulse_response("ir8", f"{IR_PATH}/BatteryTolles-L.wav", f"{IR_PATH}/BatteryTolles-R.wav")
        .start()
    )
    if piece.synth_player.should_send_to_score:
        score = piece.synth_player.supercollider_score
        score.add_message(supercollider_client.group_head(0, instrument.NodeId.SOURCE.value))
        score.add_message(supercollider_client.group_tail(NodeId.SOURCE.value, NodeId.EFFECT.value))
        score.add_message(supercollider_client.group_tail(NodeId.EFFECT.value, NodeId.ROOM_EFFECT.value))
        score.add_message(supercollider_client.load_dir(instrument.DEFAULT_SYNTH_DIR))
        score.add_message(supercollider_client.alloc_read(0, f"{SOUND_PATH}/Long Rattle 1.flac"))
        score.add_message(supercollider_client.alloc_read(1, f"{SOUND_PATH}/Long Rattle 2.flac"))
        score.add_message(supercollider_client.alloc_read(2, f"{SOUND_PATH}/Long Scratch 1.flac"))
        score.add_message(supercollider_client.alloc_read(3, f"{SOUND_PATH}/Long Scratch 2.flac"))
        score.add_message(supercollider_client.alloc_read(4, f"{SOUND_PATH}/Middle Scratch 1.flac"))
        score.add_message(supercollider_client.alloc_read(5, f"{SOUND_PATH}/Pot Hit Long 1.flac"))
        score.add_message(supercollider_client.alloc_read(6, f"{SOUND_PATH}/Pot Hit Long 2.flac"))
        score.add_message(supercollider_client.alloc_read(7, f"{SOUND_PATH}/Pot Hit Short 1.flac"))
        score.add_message(supercollider_client.alloc_read(8, f"{SOUND_PATH}/Pot Hit Short 2.flac"))
        score.add_message(supercollider_client.alloc_read(9, f"{SOUND_PATH}/Pot Hit Short 3.flac"))
        score.add_message(supercollider_client.alloc_read(10, f"{SOUND_PATH}/Pot Hit Short 4.flac"))
        score.add_message(supercollider_client.alloc_read(11, f"{SOUND_PATH}/Pot Hit Short 5.flac"))
        score.add_message(supercollider_client.alloc_read(12, f"{SOUND_PATH}/Pot Hit Short 6.flac"))
        score.add_message(supercollider_client.alloc_read(13, f"{SOUND_PATH}/Pot Hit Short 7.flac"))
        score.add_message(supercollider_client.alloc_read(14, f"{SOUND_PATH}/Pot Hit Short 8.flac"))
        score.add_message(supercollider_client.alloc_read(15, f"{SOUND_PATH}/Pot Hit Short Flam 1.flac"))
        score.add_message(supercollider_client.alloc_read(16, f"{SOUND_PATH}/Pot Hit Short Flam 2.flac"))
        score.add_message(supercollider_client.alloc_read(17, f"{SOUND_PATH}/Pot Hit Short Flam 3.flac"))
        score.add_message(supercollider_client.alloc_read(18, f"{SOUND_PATH}/Scratch Hit 1.flac"))
        score.add_message(supercollider_client.alloc_read(19, f"{SOUND_PATH}/Short Rattle Variant 1 1.flac"))
        score.add_message(supercollider_client.alloc_read(20, f"{SOUND_PATH}/Short Rattle Variant 1 2.flac"))
        score.add_message(supercollider_client.alloc_read(21, f"{SOUND_PATH}/Short Rattle Variant 1 3.flac"))
        score.add_message(supercollider_client.alloc_read(22, f"{SOUND_PATH}/Short Rattle Variant 2 1.flac"))
        score.add_message(supercollider_client.alloc_read(23, f"{SOUND_PATH}/Short Rattle Variant 2 2.flac"))
        score.add_message(supercollider_client.alloc_read(24, f"{SOUND_PATH}/Short Rattle Variant 2 3.flac"))
        score.add_message(supercollider_client.alloc_read(25, f"{SOUND_PATH}/Short Repeated Rattles 1.flac"))
        score.add_message(supercollider_client.alloc_read(26, f"{SOUND_PATH}/Short scratch 1.flac"))
        score.add_message(supercollider_client.alloc_read(27, f"{IR_PATH}/stalbans_b_ortf-L.wav"))
        score.add_message(supercollider_client.alloc_read(28, f"{IR_PATH}/stalbans_b_ortf-R.wav"))
        score.add_message(supercollider_client.alloc_read(29, f"{IR_PATH}/falkland_tennis_court_ortf-L.wav"))
        score.add_message(supercollider_client.alloc_read(30, f"{IR_PATH}/falkland_tennis_court_ortf-R.wav"))
        score.add_message(supercollider_client.alloc_read(31, f"{IR_PATH}/5UnderpassValencia-L.wav"))
        score.add_message(supercollider_client.alloc_read(32, f"{IR_PATH}/5UnderpassValencia-R.wav"))
        score.add_message(supercollider_client.alloc_read(33, f"{IR_PATH}/DrainageTunnel-L.wav"))
        score.add_message(supercollider_client.alloc_read(34, f"{IR_PATH}/DrainageTunnel-R.wav"))
        score.add_message(supercollider_client.alloc_read(35, f"{IR_PATH}/HartwellTavern-L.wav"))
        score.add_message(supercollider_client.alloc_read(36, f"{IR_PATH}/HartwellTavern-R.wav"))
        score.add_message(supercollider_client.alloc_read(37, f"{IR_PATH}/RacquetballCourt-L.wav"))
        score.add_message(supercollider_client.alloc_read(38, f"{IR_PATH}/RacquetballCourt-R.wav"))
        score.add_message(supercollider_client.alloc_read(39, f"{IR_PATH}/stalbans_a_ortf-L.wav"))
        score.add_message(supercollider_client.alloc_read(40, f"{IR_PATH}/stalbans_a_ortf-R.wav"))
        score.add_message(supercollider_client.alloc_read(41, f"{IR_PATH}/BatteryTolles-L.wav"))
        score.add_message(supercollider_client.alloc_read(42, f"{IR_PATH}/BatteryTolles-R.wav"))


high_pan_points = [(-0.99, -0.75), (0.75, 0.99)]
middle_pan_points = [(-0.66, -0.33), (0.33, 0.66)]
low_pan_points = [(-0.25, 0), (0, 0.25)]


def get_sound_duration(sound_name: str) -> float:
    return piece.synth_player.get_sound(sound_name).duration(1.0)


class PotHitShort:
    sound_group = SoundGroup.POT_HIT_SHORT

    low_ring_chain = MarkovChain(
        {
            True: {True: 0.1, False: 0.9},
            False: {True: 0.4, False: 0.6},
        },
        False,
    )

    middle_ring_chain = MarkovChain(
        {
            True: {True: 0, False: 1},
            False: {True: 0.6, False: 0.4},
        },
        False,
    )

    high_ring_chain = MarkovChain(
        {
            True: {True: 0.1, False: 0.9},
            False: {True: 0.4, False: 0.6},
        },
        False,
    )

    @classmethod
    def handle_low(cls, current_time: float, effects: list[SynthNote]) -> list[SequenceNote]:
        sound_group_sounds = sound_groups[cls.sound_group]
        sound = random.choice(sound_group_sounds)
        sound_types = sounds[sound]
        low_sound_peaks = list(set(random.choices(sound_types[SoundType.LOW], k=random_int_range(1, 2))))
        middle_sound_peaks = list(set(random.choices(sound_types[SoundType.MIDDLE], k=random_int_range(0, 1))))
        notes = []
        for pan_points, sound_peaks in [(low_pan_points, low_sound_peaks), (middle_pan_points, middle_sound_peaks)]:
            for sound_peak in sound_peaks:
                effect = random.choice(effects)
                bw = random_range(500, 600)
                static_amp_factor = 1 * random_range(0.85, 1.15)
                rq = bw / sound_peak
                amp_factor = (1 / math.sqrt(rq)) * static_amp_factor
                pan = pan_point(pan_points)
                should_ring = cls.low_ring_chain.next()
                start_time = current_time + random_range(-0.02, 0.02)
                note = (
                    piece.synth_player.note()
                    .sound_mono(str(sound), 1.0, piece.control_instruments.static_control(1.0))
                    .mono_band_pass_filter(
                        piece.control_instruments.static_control(sound_peak),
                        piece.control_instruments.static_control(rq),
                    )
                    .mono_volume(piece.control_instruments.static_control(amp_factor))
                )
                if should_ring:
                    ring = random.choice(sound_peaks)
                    note = note.ring_modulate(piece.control_instruments.static_control(ring))
                (
                    note.pan(piece.control_instruments.static_control(pan)).send_to_synth_note(
                        effect, start_time=start_time
                    )
                )
                notes.append(
                    SequenceNote(
                        start=start_time, track="Pot Hit Short Low", duration=get_sound_duration(sound), freq=sound_peak
                    )
                )
        return notes

    @classmethod
    def handle_middle(cls, current_time: float, effects: list[SynthNote]) -> list[SequenceNote]:
        sound_group_sounds = sound_groups[cls.sound_group]
        sound = random.choice(sound_group_sounds)
        sound_types = sounds[sound]
        low_sound_peaks = list(set(random.choices(sound_types[SoundType.LOW], k=random_int_range(0, 2))))
        middle_sound_peaks = list(set(random.choices(sound_types[SoundType.MIDDLE], k=random_int_range(0, 3))))
        high_sound_peaks = list(set(random.choices(sound_types[SoundType.HIGH], k=random_int_range(1, 3))))
        notes = []
        for pan_points, sound_peaks in [
            (low_pan_points, low_sound_peaks),
            (middle_pan_points, middle_sound_peaks),
            (high_pan_points, high_sound_peaks),
        ]:
            for sound_peak in sound_peaks:
                effect = random.choice(effects)
                bw = random_range(500, 600)
                # static_amp_factor = 2 * random_range(0.85, 1.15)
                static_amp_factor = 1 * random_range(0.85, 1.15)
                rq = bw / sound_peak
                amp_factor = (1 / math.sqrt(rq)) * static_amp_factor
                pan = pan_point(pan_points)
                should_ring = cls.middle_ring_chain.next()
                start_time = current_time + random_range(-0.02, 0.02)

                note = (
                    piece.synth_player.note()
                    .sound_mono(str(sound), 1.0, piece.control_instruments.static_control(1.0))
                    .mono_band_pass_filter(
                        piece.control_instruments.static_control(sound_peak),
                        piece.control_instruments.static_control(rq),
                    )
                    .mono_volume(piece.control_instruments.static_control(amp_factor))
                )
                if should_ring:
                    ring = random.choice(sound_peaks)
                    note = note.ring_modulate(piece.control_instruments.static_control(ring))
                (
                    note.pan(piece.control_instruments.static_control(pan)).send_to_synth_note(
                        effect, start_time=start_time
                    )
                )
                notes.append(
                    SequenceNote(
                        start=start_time,
                        track="Pot Hit Short Middle",
                        duration=get_sound_duration(sound),
                        freq=sound_peak,
                    )
                )
        return notes

    @classmethod
    def handle_high(cls, current_time: float, effects: list[SynthNote]) -> list[SequenceNote]:
        sound_group_sounds = sound_groups[cls.sound_group]
        sound = random.choice(sound_group_sounds)
        sound_types = sounds[sound]
        high_sound_peaks = list(set(random.choices(sound_types[SoundType.HIGH][:7], k=random_int_range(3, 7))))
        start_time = current_time + random_range(-0.02, 0.02)
        notes = []
        for pan_points, sound_peaks in [(high_pan_points, high_sound_peaks)]:
            for sound_peak in sound_peaks:
                effect = random.choice(effects)
                bw = random_range(500, 600)
                # static_amp_factor = 2 * random_range(0.85, 1.15)
                static_amp_factor = 1 * random_range(0.85, 1.15)
                rq = bw / sound_peak
                amp_factor = (1 / math.sqrt(rq)) * static_amp_factor
                pan = pan_point(pan_points)
                should_ring = cls.high_ring_chain.next()

                note = (
                    piece.synth_player.note()
                    .sound_mono(str(sound), 1.0, piece.control_instruments.static_control(1.0))
                    .mono_band_pass_filter(
                        piece.control_instruments.static_control(sound_peak),
                        piece.control_instruments.static_control(rq),
                    )
                    .mono_volume(piece.control_instruments.static_control(amp_factor))
                )
                if should_ring:
                    ring = random.choice(sound_peaks)
                    note = note.ring_modulate(piece.control_instruments.static_control(ring))
                (
                    note.mono_high_pass_filter(piece.control_instruments.static_control(min(sound_peaks)))
                    .pan(piece.control_instruments.static_control(pan))
                    .send_to_synth_note(effect, start_time=start_time)
                )
                notes.append(
                    SequenceNote(
                        start=start_time,
                        track="Pot Hit Short High",
                        duration=get_sound_duration(sound),
                        freq=sound_peak,
                    )
                )
        return notes


class ShortRattleVariant1:
    sound_group = SoundGroup.SHORT_RATTLE_VARIANT_1

    low_ring_chain = MarkovChain(
        {
            True: {True: 0.1, False: 0.9},
            False: {True: 0.4, False: 0.6},
        },
        False,
    )

    middle_ring_chain = MarkovChain(
        {
            True: {True: 0, False: 1},
            False: {True: 0.6, False: 0.4},
        },
        False,
    )

    high_ring_chain = MarkovChain(
        {
            True: {True: 0.1, False: 0.9},
            False: {True: 0.4, False: 0.6},
        },
        False,
    )

    @classmethod
    def handle_low(cls, current_time: float, effects: list[SynthNote]) -> list[SequenceNote]:
        sound_group_sounds = sound_groups[cls.sound_group]
        sound = random.choice(sound_group_sounds)
        sound_types = sounds[sound]
        low_sound_peaks = list(set(random.choices(sound_types[SoundType.LOW], k=random_int_range(1, 2))))
        middle_sound_peaks = list(set(random.choices(sound_types[SoundType.MIDDLE], k=random_int_range(0, 1))))
        notes = []
        for pan_points, sound_peaks in [(low_pan_points, low_sound_peaks), (middle_pan_points, middle_sound_peaks)]:
            for sound_peak in sound_peaks:
                effect = random.choice(effects)
                bw = random_range(500, 600)
                static_amp_factor = 3 * random_range(0.85, 1.15)
                rq = bw / sound_peak
                amp_factor = (1 / math.sqrt(rq)) * static_amp_factor
                pan = pan_point(pan_points)
                should_ring = cls.low_ring_chain.next()
                start_time = current_time + random_range(-0.02, 0.02)
                note = (
                    piece.synth_player.note()
                    .sound_mono(str(sound), 1.0, piece.control_instruments.static_control(1.0))
                    .mono_band_pass_filter(
                        piece.control_instruments.static_control(sound_peak),
                        piece.control_instruments.static_control(rq),
                    )
                    .mono_volume(piece.control_instruments.static_control(amp_factor))
                )
                if should_ring:
                    ring = random.choice(sound_peaks)
                    note = note.ring_modulate(piece.control_instruments.static_control(ring))
                (
                    note.pan(piece.control_instruments.static_control(pan)).send_to_synth_note(
                        effect, start_time=start_time
                    )
                )
                notes.append(
                    SequenceNote(
                        start=start_time,
                        track="Short rattle variant 1 low",
                        duration=get_sound_duration(sound),
                        freq=sound_peak,
                    )
                )
        return notes

    @classmethod
    def handle_middle(cls, current_time: float, effects: list[SynthNote]) -> list[SequenceNote]:
        sound_group_sounds = sound_groups[cls.sound_group]
        sound = random.choice(sound_group_sounds)
        sound_types = sounds[sound]
        low_sound_peaks = list(set(random.choices(sound_types[SoundType.LOW], k=random_int_range(0, 2))))
        middle_sound_peaks = list(set(random.choices(sound_types[SoundType.MIDDLE], k=random_int_range(0, 3))))
        high_sound_peaks = list(set(random.choices(sound_types[SoundType.HIGH], k=random_int_range(1, 3))))
        notes = []
        for pan_points, sound_peaks in [
            (low_pan_points, low_sound_peaks),
            (middle_pan_points, middle_sound_peaks),
            (high_pan_points, high_sound_peaks),
        ]:
            for sound_peak in sound_peaks:
                effect = random.choice(effects)
                bw = random_range(500, 600)
                static_amp_factor = 2 * random_range(0.85, 1.15)
                rq = bw / sound_peak
                amp_factor = (1 / math.sqrt(rq)) * static_amp_factor
                pan = pan_point(pan_points)
                should_ring = cls.middle_ring_chain.next()
                start_time = current_time + random_range(-0.02, 0.02)
                note = (
                    piece.synth_player.note()
                    .sound_mono(str(sound), 1.0, piece.control_instruments.static_control(1.0))
                    .mono_band_pass_filter(
                        piece.control_instruments.static_control(sound_peak),
                        piece.control_instruments.static_control(rq),
                    )
                    .mono_volume(piece.control_instruments.static_control(amp_factor))
                )
                if should_ring:
                    ring = random.choice(sound_peaks)
                    note = note.ring_modulate(piece.control_instruments.static_control(ring))
                (
                    note.pan(piece.control_instruments.static_control(pan)).send_to_synth_note(
                        effect, start_time=start_time
                    )
                )
                notes.append(
                    SequenceNote(
                        start=start_time,
                        track="Short rattle variant 1 middle",
                        duration=get_sound_duration(sound),
                        freq=sound_peak,
                    )
                )
        return notes

    @classmethod
    def handle_high(cls, current_time: float, effects: list[SynthNote]) -> list[SequenceNote]:
        sound_group_sounds = sound_groups[cls.sound_group]
        sound = random.choice(sound_group_sounds)
        sound_types = sounds[sound]
        high_sound_peaks = list(set(random.choices(sound_types[SoundType.HIGH][:7], k=random_int_range(3, 7))))
        notes = []
        for pan_points, sound_peaks in [(high_pan_points, high_sound_peaks)]:
            for sound_peak in sound_peaks:
                effect = random.choice(effects)
                bw = random_range(500, 600)
                static_amp_factor = 2 * random_range(0.85, 1.15)
                rq = bw / sound_peak
                amp_factor = (1 / math.sqrt(rq)) * static_amp_factor
                pan = pan_point(pan_points)
                should_ring = cls.high_ring_chain.next()
                start_time = current_time + random_range(-0.02, 0.02)
                note = (
                    piece.synth_player.note()
                    .sound_mono(str(sound), 1.0, piece.control_instruments.static_control(1.0))
                    .mono_band_pass_filter(
                        piece.control_instruments.static_control(sound_peak),
                        piece.control_instruments.static_control(rq),
                    )
                    .mono_volume(piece.control_instruments.static_control(amp_factor))
                )
                if should_ring:
                    ring = random.choice(sound_peaks)
                    note = note.ring_modulate(piece.control_instruments.static_control(ring))
                (
                    note.mono_high_pass_filter(piece.control_instruments.static_control(min(sound_peaks)))
                    .pan(piece.control_instruments.static_control(pan))
                    .send_to_synth_note(effect, start_time=start_time)
                )
                notes.append(
                    SequenceNote(
                        start=start_time,
                        track="Short rattle variant 1 high",
                        duration=get_sound_duration(sound),
                        freq=sound_peak,
                    )
                )
        return notes


class ShortRattleVariant2:
    sound_group = SoundGroup.SHORT_RATTLE_VARIANT_2

    low_ring_chain = MarkovChain(
        {
            True: {True: 0.1, False: 0.9},
            False: {True: 0.4, False: 0.6},
        },
        False,
    )

    middle_ring_chain = MarkovChain(
        {
            True: {True: 0, False: 1},
            False: {True: 0.6, False: 0.4},
        },
        False,
    )

    high_ring_chain = MarkovChain(
        {
            True: {True: 0.1, False: 0.9},
            False: {True: 0.4, False: 0.6},
        },
        False,
    )

    @classmethod
    def handle_low(cls, current_time: float, effects: list[SynthNote]) -> list[SequenceNote]:
        sound_group_sounds = sound_groups[cls.sound_group]
        sound = random.choice(sound_group_sounds)
        sound_types = sounds[sound]
        low_sound_peaks = list(set(random.choices(sound_types[SoundType.LOW], k=random_int_range(1, 2))))
        middle_sound_peaks = list(set(random.choices(sound_types[SoundType.MIDDLE], k=random_int_range(0, 1))))
        notes = []
        for pan_points, sound_peaks in [(low_pan_points, low_sound_peaks), (middle_pan_points, middle_sound_peaks)]:
            for sound_peak in sound_peaks:
                effect = random.choice(effects)
                bw = random_range(500, 600)
                static_amp_factor = 3 * random_range(0.85, 1.15)
                rq = bw / sound_peak
                amp_factor = (1 / math.sqrt(rq)) * static_amp_factor
                pan = pan_point(pan_points)
                should_ring = cls.low_ring_chain.next()
                start_time = current_time + random_range(-0.02, 0.02)
                note = (
                    piece.synth_player.note()
                    .sound_mono(str(sound), 1.0, piece.control_instruments.static_control(1.0))
                    .mono_band_pass_filter(
                        piece.control_instruments.static_control(sound_peak),
                        piece.control_instruments.static_control(rq),
                    )
                    .mono_volume(piece.control_instruments.static_control(amp_factor))
                )
                if should_ring:
                    ring = random.choice(sound_peaks)
                    note = note.ring_modulate(piece.control_instruments.static_control(ring))
                (
                    note.pan(piece.control_instruments.static_control(pan)).send_to_synth_note(
                        effect, start_time=start_time
                    )
                )
                notes.append(
                    SequenceNote(
                        start=start_time,
                        track="Short rattle variant 2 low",
                        duration=get_sound_duration(sound),
                        freq=sound_peak,
                    )
                )
        return notes

    @classmethod
    def handle_middle(cls, current_time: float, effects: list[SynthNote]) -> list[SequenceNote]:
        sound_group_sounds = sound_groups[cls.sound_group]
        sound = random.choice(sound_group_sounds)
        sound_types = sounds[sound]
        low_sound_peaks = list(set(random.choices(sound_types[SoundType.LOW], k=random_int_range(0, 2))))
        middle_sound_peaks = list(set(random.choices(sound_types[SoundType.MIDDLE], k=random_int_range(0, 3))))
        high_sound_peaks = list(set(random.choices(sound_types[SoundType.HIGH], k=random_int_range(1, 3))))
        notes = []
        for pan_points, sound_peaks in [
            (low_pan_points, low_sound_peaks),
            (middle_pan_points, middle_sound_peaks),
            (high_pan_points, high_sound_peaks),
        ]:
            for sound_peak in sound_peaks:
                effect = random.choice(effects)
                bw = random_range(500, 600)
                static_amp_factor = 2 * random_range(0.85, 1.15)
                rq = bw / sound_peak
                amp_factor = (1 / math.sqrt(rq)) * static_amp_factor
                pan = pan_point(pan_points)
                should_ring = cls.middle_ring_chain.next()
                start_time = current_time + random_range(-0.02, 0.02)
                note = (
                    piece.synth_player.note()
                    .sound_mono(str(sound), 1.0, piece.control_instruments.static_control(1.0))
                    .mono_band_pass_filter(
                        piece.control_instruments.static_control(sound_peak),
                        piece.control_instruments.static_control(rq),
                    )
                    .mono_volume(piece.control_instruments.static_control(amp_factor))
                )
                if should_ring:
                    ring = random.choice(sound_peaks)
                    note = note.ring_modulate(piece.control_instruments.static_control(ring))
                (
                    note.pan(piece.control_instruments.static_control(pan)).send_to_synth_note(
                        effect, start_time=start_time
                    )
                )
                notes.append(
                    SequenceNote(
                        start=start_time,
                        track="Short rattle variant 2 middle",
                        duration=get_sound_duration(sound),
                        freq=sound_peak,
                    )
                )
        return notes

    @classmethod
    def handle_high(cls, current_time: float, effects: list[SynthNote]) -> list[SequenceNote]:
        sound_group_sounds = sound_groups[cls.sound_group]
        sound = random.choice(sound_group_sounds)
        sound_types = sounds[sound]
        high_sound_peaks = list(set(random.choices(sound_types[SoundType.HIGH][:7], k=random_int_range(3, 7))))
        notes = []
        for pan_points, sound_peaks in [(high_pan_points, high_sound_peaks)]:
            for sound_peak in sound_peaks:
                effect = random.choice(effects)
                bw = random_range(500, 600)
                static_amp_factor = 2 * random_range(0.85, 1.15)
                rq = bw / sound_peak
                amp_factor = (1 / math.sqrt(rq)) * static_amp_factor
                pan = pan_point(pan_points)
                should_ring = cls.high_ring_chain.next()
                start_time = current_time + random_range(-0.02, 0.02)
                note = (
                    piece.synth_player.note()
                    .sound_mono(str(sound), 1.0, piece.control_instruments.static_control(1.0))
                    .mono_band_pass_filter(
                        piece.control_instruments.static_control(sound_peak),
                        piece.control_instruments.static_control(rq),
                    )
                    .mono_volume(piece.control_instruments.static_control(amp_factor))
                )
                if should_ring:
                    ring = random.choice(sound_peaks)
                    note = note.ring_modulate(piece.control_instruments.static_control(ring))
                (
                    note.mono_high_pass_filter(piece.control_instruments.static_control(min(sound_peaks)))
                    .pan(piece.control_instruments.static_control(pan))
                    .send_to_synth_note(effect, start_time=start_time)
                )
                notes.append(
                    SequenceNote(
                        start=start_time,
                        track="Short rattle variant 2 high",
                        duration=get_sound_duration(sound),
                        freq=sound_peak,
                    )
                )
        return notes


class LongScratch:
    sound_group = SoundGroup.LONG_SCRATCH
    sound_group_sounds = sound_groups[sound_group]

    high_ring_chain = MarkovChain(
        {
            True: {True: 0.1, False: 0.9},
            False: {True: 0.4, False: 0.6},
        },
        False,
    )

    middle_ring_chain = MarkovChain(
        {
            True: {True: 0, False: 1},
            False: {True: 0.6, False: 0.4},
        },
        False,
    )

    low_ring_chain = MarkovChain(
        {
            True: {True: 0.1, False: 0.9},
            False: {True: 0.4, False: 0.6},
        },
        False,
    )

    @classmethod
    def handle_high(cls, current_time: float, effects: list[SynthNote]):
        sound = random.choice(cls.sound_group_sounds)
        sound_types = sounds[sound]
        high_sound_peaks = list(set(random.choices(sound_types[SoundType.HIGH][5:], k=random_int_range(1, 7))))
        notes = []
        for pan_points, sound_peaks in [(high_pan_points, high_sound_peaks)]:
            for sound_peak in sound_peaks:
                effect = random.choice(effects)
                bw = random_range(500, 600)
                static_amp_factor = 2 * random_range(0.85, 1.15)
                rq = bw / sound_peak
                amp_factor = (1 / math.sqrt(rq)) * static_amp_factor
                pan = pan_point(pan_points)
                should_ring = cls.high_ring_chain.next()
                start_time = current_time + random_range(-0.03, 0.03)
                note = (
                    piece.synth_player.note()
                    .sound_mono(str(sound), 1.0, piece.control_instruments.static_control(1.0))
                    .mono_band_pass_filter(
                        piece.control_instruments.static_control(sound_peak),
                        piece.control_instruments.static_control(rq),
                    )
                    .mono_volume(piece.control_instruments.static_control(amp_factor))
                )
                if should_ring:
                    ring = random.choice(sound_peaks)
                    note = note.ring_modulate(piece.control_instruments.static_control(ring))
                (
                    note.mono_high_pass_filter(piece.control_instruments.static_control(min(sound_peaks)))
                    .pan(piece.control_instruments.static_control(pan))
                    .send_to_synth_note(effect, start_time=start_time)
                )
                notes.append(
                    SequenceNote(
                        start=start_time, track="Long Scratch high", duration=get_sound_duration(sound), freq=sound_peak
                    )
                )
        return notes

    @classmethod
    def handle_middle(cls, current_time: float, effects: list[SynthNote]):
        sound = random.choice(cls.sound_group_sounds)
        sound_types = sounds[sound]
        low_sound_peaks = list(set(random.choices(sound_types[SoundType.LOW], k=random_int_range(1, 2))))
        middle_sound_peaks = list(set(random.choices(sound_types[SoundType.MIDDLE], k=random_int_range(1, 2))))
        high_sound_peaks = list(set(random.choices(sound_types[SoundType.HIGH], k=random_int_range(1, 5))))
        notes = []
        for pan_points, sound_peaks in [
            (low_pan_points, low_sound_peaks),
            (middle_pan_points, middle_sound_peaks),
            (high_pan_points, high_sound_peaks),
        ]:
            for sound_peak in sound_peaks:
                effect = random.choice(effects)
                bw = random_range(500, 600)
                static_amp_factor = 2 * random_range(0.85, 1.15)
                rq = bw / sound_peak
                amp_factor = (1 / math.sqrt(rq)) * static_amp_factor
                pan = pan_point(pan_points)
                should_ring = cls.middle_ring_chain.next()
                start_time = current_time + random_range(-0.03, 0.03)
                note = (
                    piece.synth_player.note()
                    .sound_mono(str(sound), 1.0, piece.control_instruments.static_control(1.0))
                    .mono_band_pass_filter(
                        piece.control_instruments.static_control(sound_peak),
                        piece.control_instruments.static_control(rq),
                    )
                    .mono_volume(piece.control_instruments.static_control(amp_factor))
                )
                if should_ring:
                    ring = random.choice(sound_peaks)
                    note = note.ring_modulate(piece.control_instruments.static_control(ring))
                (
                    note.pan(piece.control_instruments.static_control(pan)).send_to_synth_note(
                        effect, start_time=start_time
                    )
                )
                notes.append(
                    SequenceNote(
                        start=start_time,
                        track="Long Scratch middle",
                        duration=get_sound_duration(sound),
                        freq=sound_peak,
                    )
                )
        return notes

    @classmethod
    def handle_low(cls, current_time: float, effects: list[SynthNote]):
        sound = random.choice(cls.sound_group_sounds)
        sound_types = sounds[sound]
        low_sound_peaks = list(set(random.choices(sound_types[SoundType.LOW], k=random_int_range(1, 2))))
        middle_sound_peaks = list(set(random.choices(sound_types[SoundType.MIDDLE], k=random_int_range(0, 1))))
        notes = []
        for pan_points, sound_peaks in [(low_pan_points, low_sound_peaks), (middle_pan_points, middle_sound_peaks)]:
            for sound_peak in sound_peaks:
                effect = random.choice(effects)
                bw = random_range(500, 600)
                static_amp_factor = 3 * random_range(0.85, 1.15)
                rq = bw / sound_peak
                amp_factor = (1 / math.sqrt(rq)) * static_amp_factor
                pan = pan_point(pan_points)
                should_ring = cls.low_ring_chain.next()
                start_time = current_time + random_range(-0.03, 0.03)
                note = (
                    piece.synth_player.note()
                    .sound_mono(str(sound), 1.0, piece.control_instruments.static_control(1.0))
                    .mono_band_pass_filter(
                        piece.control_instruments.static_control(sound_peak),
                        piece.control_instruments.static_control(rq),
                    )
                    .mono_volume(piece.control_instruments.static_control(amp_factor))
                )
                if should_ring:
                    ring = random.choice(sound_peaks)
                    note = note.ring_modulate(piece.control_instruments.static_control(ring))
                (
                    note.pan(piece.control_instruments.static_control(pan)).send_to_synth_note(
                        effect, start_time=start_time
                    )
                )
                notes.append(
                    SequenceNote(
                        start=start_time, track="Long Scratch low", duration=get_sound_duration(sound), freq=sound_peak
                    )
                )
        return notes


class PotHitLong:
    sound_group = SoundGroup.POT_HIT_LONG
    sound_group_sounds = sound_groups[sound_group]

    low_pot_hit_long_ring_chain = MarkovChain(
        {
            True: {True: 0.5, False: 0.5},
            False: {True: 0.9, False: 0.1},
        },
        False,
    )

    middle_pot_hit_long_ring_chain = MarkovChain(
        {
            True: {True: 0, False: 1},
            False: {True: 0.4, False: 0.6},
        },
        False,
    )

    high_pot_hit_long_ring_chain = MarkovChain(
        {
            True: {True: 0.1, False: 0.9},
            False: {True: 0.6, False: 0.4},
        },
        False,
    )

    @classmethod
    def handle_high(cls, current_time: float, effects: list[SynthNote]):
        sound = random.choice(cls.sound_group_sounds)
        sound_types = sounds[sound]
        high_sound_peaks = list(set(random.choices(sound_types[SoundType.HIGH][4:], k=random_int_range(3, 7))))
        notes = []
        for pan_points, sound_peaks in [(high_pan_points, high_sound_peaks)]:
            for sound_peak in sound_peaks:
                effect = random.choice(effects)
                bw = random_range(500, 600)
                # static_amp_factor = 2 * random_range(0.85, 1.15)
                static_amp_factor = 1.3 * random_range(0.85, 1.15)
                rq = bw / sound_peak
                amp_factor = (1 / math.sqrt(rq)) * static_amp_factor
                pan = pan_point(pan_points)
                should_ring = cls.high_pot_hit_long_ring_chain.next()
                start_time = current_time + random_range(-0.03, 0.03)
                note = (
                    piece.synth_player.note()
                    .sound_mono(str(sound), 1.0, piece.control_instruments.static_control(1.0))
                    .mono_band_pass_filter(
                        piece.control_instruments.static_control(sound_peak),
                        piece.control_instruments.static_control(rq),
                    )
                    .mono_volume(piece.control_instruments.static_control(amp_factor))
                )
                if should_ring:
                    ring = random.choice(sound_peaks)
                    note = note.ring_modulate(piece.control_instruments.static_control(ring))
                (
                    note.mono_high_pass_filter(piece.control_instruments.static_control(min(sound_peaks)))
                    .pan(piece.control_instruments.static_control(pan))
                    .send_to_synth_note(effect, start_time=start_time)
                )
                notes.append(
                    SequenceNote(
                        start=start_time, track="Pot hit long high", duration=get_sound_duration(sound), freq=sound_peak
                    )
                )
        return notes

    @classmethod
    def handle_middle(cls, current_time: float, effects: list[SynthNote]):
        sound = random.choice(cls.sound_group_sounds)
        sound_types = sounds[sound]
        low_sound_peaks = list(set(random.choices(sound_types[SoundType.LOW], k=random_int_range(1, 2))))
        middle_sound_peaks = list(set(random.choices(sound_types[SoundType.MIDDLE], k=random_int_range(1, 2))))
        high_sound_peaks = list(set(random.choices(sound_types[SoundType.HIGH], k=random_int_range(1, 5))))
        notes = []
        for pan_points, sound_peaks in [
            (low_pan_points, low_sound_peaks),
            (middle_pan_points, middle_sound_peaks),
            (high_pan_points, high_sound_peaks),
        ]:
            for sound_peak in sound_peaks:
                effect = random.choice(effects)
                bw = random_range(500, 600)
                static_amp_factor = 2 * random_range(0.85, 1.15)
                rq = bw / sound_peak
                amp_factor = (1 / math.sqrt(rq)) * static_amp_factor
                pan = pan_point(pan_points)
                should_ring = cls.middle_pot_hit_long_ring_chain.next()
                start_time = current_time + random_range(-0.03, 0.03)
                note = (
                    piece.synth_player.note()
                    .sound_mono(str(sound), 1.0, piece.control_instruments.static_control(1.0))
                    .mono_band_pass_filter(
                        piece.control_instruments.static_control(sound_peak),
                        piece.control_instruments.static_control(rq),
                    )
                    .mono_volume(piece.control_instruments.static_control(amp_factor))
                )
                if should_ring:
                    ring = random.choice(sound_peaks)
                    note = note.ring_modulate(piece.control_instruments.static_control(ring))

                (
                    note.pan(piece.control_instruments.static_control(pan)).send_to_synth_note(
                        effect, start_time=start_time
                    )
                )
                notes.append(
                    SequenceNote(
                        start=start_time,
                        track="Pot hit long middle",
                        duration=get_sound_duration(sound),
                        freq=sound_peak,
                    )
                )
            return notes

    @classmethod
    def handle_low(cls, current_time: float, effects: list[SynthNote]):
        sound = random.choice(cls.sound_group_sounds)
        sound_types = sounds[sound]
        low_sound_peaks = list(set(random.choices(sound_types[SoundType.LOW], k=random_int_range(1, 2))))
        middle_sound_peaks = list(set(random.choices(sound_types[SoundType.MIDDLE], k=random_int_range(0, 1))))
        notes = []
        for pan_points, sound_peaks in [(low_pan_points, low_sound_peaks), (middle_pan_points, middle_sound_peaks)]:
            for sound_peak in sound_peaks:
                effect = random.choice(effects)
                bw = random_range(500, 600)
                static_amp_factor = 1 * random_range(0.85, 1.15)
                rq = bw / sound_peak
                amp_factor = (1 / math.sqrt(rq)) * static_amp_factor
                pan = pan_point(pan_points)
                should_ring = cls.low_pot_hit_long_ring_chain.next()
                start_time = current_time + random_range(-0.03, 0.03)
                note = (
                    piece.synth_player.note()
                    .sound_mono(str(sound), 1.0, piece.control_instruments.static_control(1.0))
                    .mono_band_pass_filter(
                        piece.control_instruments.static_control(sound_peak),
                        piece.control_instruments.static_control(rq),
                    )
                    .mono_volume(piece.control_instruments.static_control(amp_factor))
                )
                if should_ring:
                    ring = random.choice(sound_peaks)
                    note = note.ring_modulate(piece.control_instruments.static_control(ring))

                (
                    note.pan(piece.control_instruments.static_control(pan)).send_to_synth_note(
                        effect, start_time=start_time
                    )
                )
                notes.append(
                    SequenceNote(
                        start=start_time, track="Pot hit long low", duration=get_sound_duration(sound), freq=sound_peak
                    )
                )
        return notes


class ShortPotHitRattleGroup:
    low_sound_group_chain = MarkovChain(
        {
            SoundGroup.POT_HIT_SHORT: {
                SoundGroup.POT_HIT_SHORT: 0,
                SoundGroup.SHORT_RATTLE_VARIANT_1: 0.5,
                SoundGroup.SHORT_RATTLE_VARIANT_2: 0.5,
            },
            SoundGroup.SHORT_RATTLE_VARIANT_1: {
                SoundGroup.POT_HIT_SHORT: 0.5,
                SoundGroup.SHORT_RATTLE_VARIANT_1: 0.2,
                SoundGroup.SHORT_RATTLE_VARIANT_2: 0.3,
            },
            SoundGroup.SHORT_RATTLE_VARIANT_2: {
                SoundGroup.POT_HIT_SHORT: 0.5,
                SoundGroup.SHORT_RATTLE_VARIANT_1: 0.3,
                SoundGroup.SHORT_RATTLE_VARIANT_2: 0.2,
            },
        },
        SoundGroup.POT_HIT_SHORT,
    )

    middle_sound_group_chain = MarkovChain(
        {
            SoundGroup.POT_HIT_SHORT: {
                SoundGroup.POT_HIT_SHORT: 0.4,
                SoundGroup.SHORT_RATTLE_VARIANT_1: 0.3,
                SoundGroup.SHORT_RATTLE_VARIANT_2: 0.3,
            },
            SoundGroup.SHORT_RATTLE_VARIANT_1: {
                SoundGroup.POT_HIT_SHORT: 0.6,
                SoundGroup.SHORT_RATTLE_VARIANT_1: 0.1,
                SoundGroup.SHORT_RATTLE_VARIANT_2: 0.3,
            },
            SoundGroup.SHORT_RATTLE_VARIANT_2: {
                SoundGroup.POT_HIT_SHORT: 0.6,
                SoundGroup.SHORT_RATTLE_VARIANT_1: 0.3,
                SoundGroup.SHORT_RATTLE_VARIANT_2: 0.1,
            },
        },
        SoundGroup.POT_HIT_SHORT,
    )

    high_sound_group_chain = MarkovChain(
        {
            SoundGroup.POT_HIT_SHORT: {
                SoundGroup.POT_HIT_SHORT: 0.2,
                SoundGroup.SHORT_RATTLE_VARIANT_1: 0.4,
                SoundGroup.SHORT_RATTLE_VARIANT_2: 0.4,
            },
            SoundGroup.SHORT_RATTLE_VARIANT_1: {
                SoundGroup.POT_HIT_SHORT: 0.4,
                SoundGroup.SHORT_RATTLE_VARIANT_1: 0.2,
                SoundGroup.SHORT_RATTLE_VARIANT_2: 0.4,
            },
            SoundGroup.SHORT_RATTLE_VARIANT_2: {
                SoundGroup.POT_HIT_SHORT: 0.4,
                SoundGroup.SHORT_RATTLE_VARIANT_1: 0.4,
                SoundGroup.SHORT_RATTLE_VARIANT_2: 0.2,
            },
        },
        SoundGroup.POT_HIT_SHORT,
    )

    @classmethod
    def play_low_group(cls, time: float, effects: list[SynthNote]) -> tuple[int, list[SequenceNote]]:
        current_time = time
        number_of_notes = random_int_range(1, 2)
        notes = []
        for _ in range(number_of_notes):            
            sound_group = cls.low_sound_group_chain.next()
            match sound_group:
                case SoundGroup.POT_HIT_SHORT:
                    notes.extend(PotHitShort.handle_low(current_time, effects))
                case SoundGroup.SHORT_RATTLE_VARIANT_1:
                    notes.extend(ShortRattleVariant1.handle_low(current_time, effects))
                case SoundGroup.SHORT_RATTLE_VARIANT_2:
                    notes.extend(ShortRattleVariant2.handle_low(current_time, effects))
            current_time += random_range(0.05, 0.2)
        return number_of_notes, notes

    @classmethod
    def play_middle_group(cls, time: float, effects: list[SynthNote]) -> tuple[int, list[SequenceNote]]:

        current_time = time
        number_of_notes = random_int_range(1, 3)
        notes = []
        for _ in range(number_of_notes):
            sound_group = cls.middle_sound_group_chain.next()
            match sound_group:
                case SoundGroup.POT_HIT_SHORT:
                    notes.extend(PotHitShort.handle_middle(current_time, effects))
                case SoundGroup.SHORT_RATTLE_VARIANT_1:
                    notes.extend(ShortRattleVariant1.handle_middle(current_time, effects))
                case SoundGroup.SHORT_RATTLE_VARIANT_2:
                    notes.extend(ShortRattleVariant2.handle_middle(current_time, effects))
            current_time += random_range(0.05, 0.2)
        return number_of_notes, notes

    @classmethod
    def play_high_group(cls, time: float, effects: list[SynthNote]) -> tuple[int, list[SequenceNote]]:
        current_time = time
        number_of_notes = random_int_range(1, 3)
        notes = []
        for _ in range(number_of_notes):
            sound_group = cls.high_sound_group_chain.next()
            match sound_group:
                case SoundGroup.POT_HIT_SHORT:
                    notes.extend(PotHitShort.handle_high(current_time, effects))
                case SoundGroup.SHORT_RATTLE_VARIANT_1:
                    notes.extend(ShortRattleVariant1.handle_high(current_time, effects))
                case SoundGroup.SHORT_RATTLE_VARIANT_2:
                    notes.extend(ShortRattleVariant2.handle_high(current_time, effects))
            current_time += random_range(0.05, 0.2)
        return number_of_notes, notes


class PotHitScratchGroup:
    low_sound_group_chain = MarkovChain(
        {
            SoundGroup.POT_HIT_LONG: {SoundGroup.POT_HIT_LONG: 0, SoundGroup.LONG_SCRATCH: 1},
            SoundGroup.LONG_SCRATCH: {SoundGroup.POT_HIT_LONG: 0.3, SoundGroup.LONG_SCRATCH: 0.7},
        },
        SoundGroup.POT_HIT_LONG,
    )

    middle_sound_group_chain = MarkovChain(
        {
            SoundGroup.POT_HIT_LONG: {SoundGroup.POT_HIT_LONG: 0, SoundGroup.LONG_SCRATCH: 1},
            SoundGroup.LONG_SCRATCH: {SoundGroup.POT_HIT_LONG: 0.3, SoundGroup.LONG_SCRATCH: 0.7},
        },
        SoundGroup.POT_HIT_LONG,
    )

    high_sound_group_chain = MarkovChain(
        {
            SoundGroup.POT_HIT_LONG: {SoundGroup.POT_HIT_LONG: 0, SoundGroup.LONG_SCRATCH: 1},
            SoundGroup.LONG_SCRATCH: {SoundGroup.POT_HIT_LONG: 0.3, SoundGroup.LONG_SCRATCH: 0.7},
        },
        SoundGroup.POT_HIT_LONG,
    )

    @classmethod
    def play_low_group(cls, time: float, effects: list[SynthNote]) -> tuple[int, list[SequenceNote]]:
        current_time = time
        number_of_notes = random_int_range(1, 2)
        notes = []
        for _ in range(number_of_notes):
            sound_group = cls.low_sound_group_chain.next()
            match sound_group:
                case SoundGroup.POT_HIT_LONG:
                    notes.extend(PotHitLong.handle_low(current_time, effects))
                case SoundGroup.LONG_SCRATCH:
                    notes.extend(LongScratch.handle_low(current_time, effects))
            current_time += random_range(0.05, 0.3)
        return number_of_notes, notes

    @classmethod
    def play_middle_group(cls, time: float, effects: list[SynthNote]) -> tuple[int, list[SequenceNote]]:
        current_time = time
        number_of_notes = random_int_range(1, 3)
        notes = []
        for _ in range(number_of_notes):
            sound_group = cls.middle_sound_group_chain.next()
            match sound_group:
                case SoundGroup.POT_HIT_LONG:
                    notes.extend(PotHitLong.handle_middle(current_time, effects))
                case SoundGroup.LONG_SCRATCH:
                    notes.extend(LongScratch.handle_middle(current_time, effects))
            current_time += random_range(0.05, 0.2)
        return number_of_notes, notes

    @classmethod
    def play_high_group(cls, time: float, effects: list[SynthNote]) -> tuple[int, list[SequenceNote]]:
        current_time = time
        number_of_notes = random_int_range(1, 3)
        notes = []
        for _ in range(number_of_notes):
            sound_group = cls.high_sound_group_chain.next()
            match sound_group:
                case SoundGroup.POT_HIT_LONG:
                    notes.extend(PotHitLong.handle_high(current_time, effects))
                case SoundGroup.LONG_SCRATCH:
                    notes.extend(LongScratch.handle_high(current_time, effects))
            current_time += random_range(0.05, 0.2)
        return number_of_notes, notes


LOW_POT_HIT_SCRATCH_IR = "ir8"
MIDDLE_POT_HIT_SCRATCH_IR = "ir2"
HIGH_POT_HIT_SCRATCH_IR = "ir4"
LOW_SHORT_POT_HIT_RATTLE_IR = "ir6"
MIDDLE_SHORT_POT_HIT_RATTLE_IR = "ir1"
HIGH_SHORT_POT_HIT_RATTLE_IR = "ir7"
