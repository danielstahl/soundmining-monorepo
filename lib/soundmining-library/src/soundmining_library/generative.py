import random
from typing import TypeVar, Generic


def random_range(min: float, max: float) -> float:
    return random.uniform(min, max)


def random_int_range(min: int, max: int) -> int:
    return random.randint(min, max)


T = TypeVar('T')


def pick_items(items: list[T], size: int) -> list[T]:
    return random.choices(items, k=size)


class WeightedRandom(Generic[T]):

    def make_sorted_pairs(self,
                          pairs: list[tuple[T, float]]) -> list[tuple[T, float]]:
        probability_sum = 0
        for (value, probability) in pairs:
            probability_sum = probability_sum + probability
        fact = 1.0 / probability_sum
        result = []
        for (value, probability) in pairs:
            result.append((value, probability * fact))
        return result

    def __init__(self, pairs: list[tuple[T, float]]) -> None:
        self.sorted_pairs = self.make_sorted_pairs(pairs)

    def choose_value(self, weighted_random: float,
                     pairs_to_choose: list[tuple[T, float]]) -> T:
        head, *tail = pairs_to_choose
        (head_item, head_probbility) = head
        if weighted_random <= head_probbility:
            return head_item
        else:
            return self.choose_value(weighted_random - head_probbility, tail)

    def choose(self) -> T:
        return self.choose_value(random.random(), self.sorted_pairs)


class MarkovChain(Generic[T]):

    def __init__(self, transition_matrix: dict[T, dict[T, float]], initial_value: T) -> None:
        self.transition_matrix = self.scale_transition_matrix(transition_matrix)
        self.current_value = initial_value

    def scale_transition_matrix(self, transition_matrix: dict[T, dict[T, float]]) -> dict[T, dict[T, float]]:
        scaled_matrix = {}
        for i, matrix in transition_matrix.items():
            ratio = 1 / sum(matrix.values())
            scaled_transition = {}
            for n, weight in matrix.items():
                scaled_transition[n] = weight * ratio
            scaled_matrix[i] = scaled_transition
        return scaled_matrix

    def next(self) -> T:
        current_transision = self.transition_matrix[self.current_value]
        next_value = random.choices(population=list(current_transision.keys()), weights=list(current_transision.values()), k=1)[0]
        self.current_value = next_value
        return next_value

    def sum_transition_matrix(self) -> dict[T, float]:
        summed_matrix = {}
        for matrix in self.transition_matrix.values():
            for n, weight in matrix.items():
                summed_matrix[n] = summed_matrix.get(n, 0) + weight
        return summed_matrix


def pan_line(distance: float, ranges: list[tuple[float, float]] = [(-0.99, 0.99)]) -> tuple[float, float]:
    range_start, range_end = random.choices(ranges, k=1)[0]
    random_distance = distance * random_range(0.8, 1.2)
    starting_point = random_range(range_start, range_end)
    direction = random.choice([-1.0, 1.0])
    desired_endpoint = (starting_point + random_distance) * direction
    endpoint = max(min(desired_endpoint, range_end), range_start)
    return (starting_point, endpoint)


def pan_point(ranges: list[tuple[float, float]] = [(-0.99, 0.99)]) -> float:
    range_start, range_end = random.choices(ranges, k=1)[0]
    return random_range(range_start, range_end)

# Make dynamic generative that change probability over time.
# Initiall support static and line. Also be able to chain into
# sequences.
# Support markov chain, choice, range, weighted random.
