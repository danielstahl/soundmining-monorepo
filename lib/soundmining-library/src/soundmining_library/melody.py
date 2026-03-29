def transpose(amount: int, melody: list[int]) -> list[int]:
    return [note + amount for note in melody]


def shift(amount: int, melody: list[int]) -> list[int]:
    return melody[amount:] + melody[:amount]


def makeIntervals(melody: list[int]) -> list[int]:
    lastItem, *melodyTail = melody
    result = [lastItem]
    for item in melodyTail:
        interval = item - lastItem
        lastItem = item
        result.append(interval)
    return result


def inverse(melody: list[int]) -> list[int]:
    last, *intervals = makeIntervals(melody)
    result = [last]
    for item in intervals:
        tmp = last + (item * -1)
        last = tmp
        result.append(tmp)
    return result


def retrograde(melody: list) -> list:
    return list(reversed(melody))


def concrete(indices: list[int], spectrum: list[float]) -> list[float]:
    return list(map(lambda item: spectrum[item], indices))


def absolute(start: float, relative: list[float]) -> list[float]:
    tmp = start
    result_list = []
    for time in relative:
        result = tmp
        tmp = tmp + time
        result_list.append(result)
    return result_list
