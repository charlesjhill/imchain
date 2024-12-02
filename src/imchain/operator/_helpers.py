import functools
import inspect
import logging

import typing_extensions as tp

logger = logging.getLogger(__name__)


def num_required_args(f):
    """Get the number of required arguments to `f`.

    Raises:
        ValueError: If a function signature cannot be inferred from `f`.
    """
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


def _with_no_args(x, f):
    return f()


def zero_or_one_args(
    f: tp.Union[tp.Callable[[tp.Any], U], tp.Callable[[], U], None] = None,
) -> tp.Callable[[tp.Any], U]:
    """Convert a callable with 0/1 arguments into a 1 argument callable."""
    if f is None:
        # Support @zero_or_one_args and @zero_or_one_args()
        return zero_or_one_args

    try:
        num_args = num_required_args(f)
    except ValueError:
        # If we cannot determine the number of arguments of `f`, just return the
        # object. Hope it's 1 argument!
        logger.warning("Could not infer function signature from %s.", f, exc_info=True)
        return f

    if num_args == 0:
        return functools.partial(_with_no_args, f=f)

    if num_args == 1:
        return f

    msg = f"Expected `f` to have 1 or fewer required arguments. It had {num_args}."
    raise ValueError(msg)


def check_callable(caller, arg, *, arg_name="func"):
    if callable(arg):
        return

    msg = f"Expected {caller.__class__.__name__}.{arg_name} to be a callable, but got {type(arg)}."
    raise ValueError(msg)
