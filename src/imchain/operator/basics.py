import typing_extensions as tp

from ._helpers import check_callable, zero_or_one_args
from .core import Operator

T = tp.TypeVar("T")
U = tp.TypeVar("U")
V = tp.TypeVar("V")

__all__ = ("Effect", "Filter", "Map", "Noop")

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


class Where(Operator[T, tp.Union[U, V]]):
    """Operator to switch an operation based on the result of a predicate function.

    Can be configured at init time or via a fluent interface.

    Examples:
        >>> chain = Where(lambda x: x % 2 == 0).then(lambda x: x // 2).otherwise(lambda x: 3*x+1)
        >>> assert chain.process([0, 1, 2, 3]) == [0, 4, 2, 10]
    """

    def __init__(
        self,
        predicate: tp.Callable[[T], bool],
        then: tp.Union[Operator[T, U], tp.Callable[[T], U], None] = None,
        otherwise: tp.Union[Operator[T, V], tp.Callable[[T], V], None] = None,
    ):
        self.predicate = predicate
        self.then(then).otherwise(otherwise)

    def then(self, op: tp.Union[Operator[T, U], tp.Callable[[T], U], None]):
        if op is None:
            self.then_op = Noop()
        elif callable(op):
            self.then_op = Map(op)
        else:
            self.then_op = op

        return self

    def otherwise(self, op: tp.Union[Operator[T, V], tp.Callable[[T], V], None]):
        if op is None:
            self.otherwise_op = Noop()
        elif callable(op):
            self.otherwise_op = Map(op)
        else:
            self.otherwise_op = op

        return self

    def pipe(self, iterable: tp.Iterable[T]) -> tp.Generator[tp.Union[U, V], None, None]:
        for elem in iterable:
            if self.predicate(elem):
                yield from self.then_op.send_to_tuple(elem)
            else:
                yield from self.otherwise_op.send_to_tuple(elem)
