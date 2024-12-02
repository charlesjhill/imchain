import typing_extensions as tp

from .basics import Map
from .core import Operator, Pipeline

T = tp.TypeVar("T")
U = tp.TypeVar("U")

__all__ = ["Buffer", "Chain", "FlatMap"]

# TODO: implement __str__ and __repr__ for everything.


class Buffer(Operator[T, tp.Iterable[T]]):
    """Operator which buffers inputs."""

    def __init__(
        self,
        buffer_size: int,
        *,
        drop_last=False,
        sink: tp.Callable[[list[T]], tp.Iterable[T]] = tuple,
    ):
        """
        Args:
            buffer_size: Desired buffer size.
            drop_last: Flag to exclude the last buffer if it is not `buffer_size` long.
            sink: An Iterable constructor for the yielded buffers., or a callable which
                converts list[T] to an Iterable[T].
        """
        self.buffer_size = buffer_size
        self.drop_last = drop_last
        self.sink = sink

    def pipe(self, iterable: tp.Iterable[T]) -> tp.Generator[tp.Iterable[T], None, None]:
        buffer = []
        for item in iterable:
            buffer.append(item)
            if len(buffer) == self.buffer_size:
                yield self.sink(buffer)
                buffer.clear()

        if buffer and not self.drop_last:
            yield self.sink(buffer)
            buffer.clear()


class Chain(Operator[tp.Iterable[T], T]):
    """Operator that 'flattens' a source iterable."""

    def pipe(self, iterable: tp.Iterable[tp.Iterable[T]]) -> tp.Generator[T, None, None]:
        for subiter in iterable:
            yield from subiter


def FlatMap(func: tp.Callable[[T], tp.Iterable[U]]) -> Pipeline[T, U]:
    """An operator which combines Map with Chain.

    Examples:

        >>> op = FlatMap(lambda x: (x, x))
        >>> op.process(range(3)) == [0, 0, 1, 1, 2, 2]
        True
    """
    return Map(func) | Chain()
