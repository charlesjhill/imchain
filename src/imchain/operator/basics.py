import typing_extensions as tp

from ._helpers import check_callable, zero_or_one_args
from .core import Operator

T = tp.TypeVar("T")
U = tp.TypeVar("U")

__all__ = ["Map", "Filter", "Effect", "Noop"]

# TODO: implement __str__ and __repr__ for everything.


class Map(Operator[T, U]):
    """Applies a function to each element of an iterable."""

    def __init__(self, func: tp.Callable[[T], U]) -> None:
        check_callable(self, func)
        self.func = func

    def pipe(self, iterable):
        yield from map(self.func, iterable)


class Filter(Operator[T, T]):
    """Filter out one or more elements of an iterable."""

    def __init__(self, predicate: tp.Optional[tp.Callable[[T], bool]]) -> None:
        self.predicate = predicate

    def pipe(self, iterable):
        yield from filter(self.predicate, iterable)


class Effect(Operator[T, T]):
    """Perform a side-effect for each element of an iterable."""

    def __init__(self, func: tp.Union[tp.Callable[[T], tp.Any], tp.Callable[[], tp.Any]]):
        check_callable(self, func)

        self.func = zero_or_one_args(func)

    def pipe(self, iterable):
        for item in iterable:
            self.func(item)
            yield item


class Noop(Operator[T, T]):
    """A do-nothing operator for testing or dynamic replacement of other operators."""
    def pipe(self, iterable: tp.Iterable[T]) -> tp.Generator[T, None, None]:
        yield from iterable