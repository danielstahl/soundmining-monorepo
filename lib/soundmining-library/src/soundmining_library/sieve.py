from abc import ABC, abstractmethod


class Sieve(ABC):
    @abstractmethod
    def is_sieve(self, index: int) -> bool:
        pass


class SimpleSieve(Sieve):
    def __init__(self, step: int, offset: int) -> None:
        self.step = step
        self.offset = offset

    def is_sieve(self, index: int) -> bool:
        return (index + self.offset) % self.step == 0


class UnionSieve(Sieve):
    def __init__(self, sieves: list[Sieve]) -> None:
        self.sieves = sieves

    def is_sieve(self, index: int) -> bool:
        for sieve in self.sieves:
            if sieve.is_sieve(index):
                return True
        return False


class IntersectionSieve(Sieve):
    def __init__(self, sieves: list[Sieve]) -> None:
        self.sieves = sieves

    def is_sieve(self, index: int) -> bool:
        for sieve in self.sieves:
            if not sieve.is_sieve(index):
                return False
        return True
