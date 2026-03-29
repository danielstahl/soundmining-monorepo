def make_spectrum(fundamental: float, fact: float, size: int) -> list[float]:
    result = []
    for i in range(1, size + 1):
        multiplier = ((i - 1) * fact) + 1
        result.append(fundamental * multiplier)
    return result


# make undertone series
# Sub harmonic series
def make_undertone_spectrum(fundamental: float, fact: float, size: int) -> list[float]:
    result = []
    for i in range(1, size + 1):
        multiplier = ((i - 1) * fact) + 1
        result.append(fundamental / multiplier)
    return result


def make_fm_synthesis(carrier: float,
                      modulator: float,
                      size: int) -> list[tuple[float, float]]:
    result = []
    for i in range(0, size):
        first_sideband = abs(carrier + (i * modulator))
        second_sideband = abs(carrier - (i * modulator))
        result.append((first_sideband, second_sideband))
    return result


def make_fact(fundamental: float, first_partial: float) -> float:
    return (first_partial / fundamental) - 1


def ring_modulate(carrier: float, modulator: float) -> tuple[float, float]:
    return (carrier + modulator, carrier - modulator)
