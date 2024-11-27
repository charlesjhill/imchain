import itertools

import typing_extensions as tp

from .core import Operator

T = tp.TypeVar("T")


__all__ = (
    "Slice",
    "Take",
    "Skip",
)


class Slice(Operator[T, T]):
    def __init__(self, start=None, stop=None, step=None):
        self.start = start
        self.stop = stop
        self.step = step

    def pipe(self, iterable: tp.Iterable[T]) -> tp.Generator[T, None, None]:
        yield from itertools.islice(iterable, self.start, self.stop, self.step)


class Take(Slice[T]):
    def __init__(self, n: int):
        super().__init__(stop=n)


class Skip(Slice[T]):
    def __init__(self, n: int):
        super().__init__(start=n)
