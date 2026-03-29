import math
import re

REF_FREQ: float = 16.3516
LOG_TWO: float = math.log(2)
NOTE_PATTERN = "([ABCDEFGHabcdefgh]){1}(iss|ess)?(\\d){1}"

NATRUAL_NOTE_CENTS = {
    'c': 0,
    'd': 200,
    'e': 400,
    'f': 500,
    'g': 700,
    'a': 900,
    'h': 1100
}

MODIFIER_CENTS = {
    'iss': 100,
    'ess': -100,
    'natural': 0
}

OCTAVE_CENTS = 1200


def note_to_hertz(note: str) -> float:
    matches = re.search(NOTE_PATTERN, note)
    note_name = matches.group(1).lower()
    modifier = (matches.group(2) or "natural").lower()
    octave = matches.group(3)

    natrual_cents = NATRUAL_NOTE_CENTS[note_name]
    modifier_cents = MODIFIER_CENTS[modifier]
    octave_cents = int(octave) * OCTAVE_CENTS

    absolut_cents = octave_cents + natrual_cents + modifier_cents
    return cents_to_hertz(absolut_cents, round_result=False)


def cents_to_hertz(absolut_cents: float, round_result: bool = False) -> float:
    result = REF_FREQ * math.pow(2, absolut_cents / 1200.0)
    return round(result) if round_result else result


def hertz_to_cents(hertz: float) -> float:
    return 1200.0 * math.log(hertz / REF_FREQ) / LOG_TWO


A_PITCH = 440.0


def midi_to_hertz(midi_note: int) -> float:
    return (A_PITCH / 32) * pow(2, (midi_note - 9) / 12.00)
