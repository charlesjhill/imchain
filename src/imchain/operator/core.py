import abc

import typing_extensions as tp

T = tp.TypeVar("T")
U = tp.TypeVar("U")
V = tp.TypeVar("V")

# TODO: implement __str__ and __repr__ for everything.


class Operator(abc.ABC, tp.Generic[T, U]):
    """A stream operator.

    Stream operators apply transformations and/or filters
    to an iterable of data. The main entry point is `pipe`,
    which wraps another iterable. A few convenience functions
    are defined: `process`, `send`, and `drain`.

    - `process`: Pipes an iterable through the Operator into a sink, such `min` or `list`.
    - `send`: Pipes a single value through the Operator.
    - `drain`: Empties an iterable through the Operator, without capturing any results.

    Operators can be chained by using the binary OR operator. For example, 
    OperatorA | OperatorB produces another Operator which applies A then B.

    Operator[T, U] refers to an operator which
    transforms elements of type T into elements of U.
    Thus, Operator[T, T] is an operator which
    does not change the type of elements passing through it.
    """

    @abc.abstractmethod
    def pipe(self, iterable: tp.Iterable[T]) -> tp.Generator[U]:
        """Transform or filter an iterable through this Operator.

        Args:
            iterable: An iterable of values.

        Yields:
            A filtered or transformed iterable.
        """

    def process(self, iterable: tp.Iterable[T], sink: tp.Callable[[tp.Iterable[U]], V] = list) -> V:
        """Sugar around sink(self.pipe(iterable))."""
        return sink(self.pipe(iterable))

    def send(self, value: T) -> U:
        """Send a single value through the Operator."""
        return next(self.pipe([value]))
    
    def drain(self, iterable: tp.Iterable[T]) -> None:
        """Drain a given iterable through this Operator."""
        for _ in self.pipe(iterable):
            pass

    def __or__(self, other: "Operator"):
        # self | other
        if not isinstance(other, Operator):
            # If other is a Pipeline, let it handle the combination
            return NotImplemented

        return Pipeline(self, other)


class Pipeline(Operator[T, U], tp.MutableSequence[Operator]):
    def __init__(self, *operators: Operator):
        self.operators = list(operators)

    def pipe(self, iterable):
        for operator in self.operators:
            iterable = operator.pipe(iterable)
        yield from iterable

    # ---- Support Chaining ----

    def __or__(self, other: Operator):
        # self | other
        if not isinstance(other, Operator):
            return NotImplemented

        if isinstance(other, Pipeline):
            return Pipeline(*self.operators, *other.operators)

        return Pipeline(*self.operators, other)

    def __ror__(self, other: Operator):
        # other | self
        if not isinstance(other, Operator):
            return NotImplemented

        # other is unknown Operator
        return Pipeline(other, *self.operators)

    def __ior__(self, other: Operator):
        # self |= other
        if not isinstance(other, Operator):
            return NotImplemented

        if isinstance(other, Pipeline):
            self.operators.extend(other.operators)
        else:
            self.operators.append(other)

        return self

    # ---- MutableSequence ----
    def __getitem__(self, idx):
        operators = self.operators[idx]
        try:
            return Pipeline(*operators)
        except SyntaxError:
            return operators

    def __setitem__(self, idx, val):
        self.operators[idx] = val

    def __delitem__(self, idx):
        del self.operators[idx]

    def __len__(self):
        return len(self.operators)

    def insert(self, idx, val):
        return self.operators.insert(idx, val)

