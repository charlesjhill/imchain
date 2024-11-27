import functools
import inspect

import typing_extensions as tp


def num_required_args(f):
    """Get the number of required arguments to `f`."""
    signature = inspect.signature(f)

    empty = inspect.Signature.empty
    pk = inspect.Parameter
    search_kinds = frozenset((pk.POSITIONAL_ONLY, pk.POSITIONAL_OR_KEYWORD, pk.KEYWORD_ONLY))
    return sum(
        (param.kind in search_kinds and param.default is empty)
        for param in signature.parameters.values()
    )


T = tp.TypeVar("T")
U = tp.TypeVar("U")


def zero_or_one_args(
    f: tp.Union[tp.Callable[[tp.Any], U], tp.Callable[[], U], None] = None,
) -> tp.Callable[[tp.Any], U]:
    """Convert a callable with 0/1 arguments into a 1 argument callable."""
    if f is None:
        return zero_or_one_args

    num_args = num_required_args(f)
    if num_args == 0:

        @functools.wraps(f)
        def wrapper(x):
            return f()

        return wrapper

    if num_args == 1:
        return f

    msg = f"Expected `f` to have 1 or fewer required arguments. It had {num_args}."
    raise ValueError(msg)


def check_callable(caller, arg, *, arg_name="func"):
    if callable(arg):
        return

    msg = f"Expected {caller.__class__.__name__}.{arg_name} to be a callable, but got {type(arg)}."
    raise ValueError(msg)
