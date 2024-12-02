import itertools

import typing_extensions as tp

from .core import Operator

T = tp.TypeVar("T")


__all__ = (
    "Skip",
    "Slice",
    "Take",
)


class Slice(Operator[T, T]):
    """Operator to apply slicing to an iterable."""

    def __init__(self, start=None, stop=None, step=None):
        self.start = start
        self.stop = stop
        self.step = step

    def pipe(self, iterable: tp.Iterable[T]) -> tp.Generator[T, None, None]:
        yield from itertools.islice(iterable, self.start, self.stop, self.step)

        if isinstance(iterable, tp.Generator):
            iterable.close()


class Take(Slice[T]):
    """Operator to take the first `n`."""

    def __init__(self, n: int):
        super().__init__(stop=n)


class Skip(Slice[T]):
    """Operator to skip the first `n` elements."""

    def __init__(self, n: int):
        super().__init__(start=n)
