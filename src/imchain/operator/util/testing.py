"""Operators that are useful for testing."""

import random
import time
from functools import partial

import typing_extensions as tp

from ..basics import Effect, Filter

__all__ = (
    "Log",
    "Wait",
    "WaitData",
    "WaitRandom",
)

# Define our own wrappers at the global namespace to assist pickling.


def _random_wait(rng):
    time.sleep(rng.random())


def _inv_sleeper(x, offset):
    time.sleep(offset - x)


def _sleep(t):
    time.sleep(t)


# Actual objects


class Wait(Effect):
    def __init__(self, t=0.0):
        super().__init__(partial(_sleep, t))


class WaitRandom(Effect):
    def __init__(self, seed=314):
        rng = random.Random(seed)
        super().__init__(partial(_random_wait, rng))


class WaitData(Effect):
    def __init__(self, inverse_time: tp.Union[int, float] = 0):
        if inverse_time:
            func = partial(_inv_sleeper, offset=inverse_time)
        else:
            func = _sleep
        super().__init__(func)


def _printer(spacer):
    def log(x):
        print(f"{spacer}{x}")

    return log


class Log(Effect):
    def __init__(self, spacers: int = 0):
        spacer = "-" * spacers
        if spacer:
            spacer += " "
        super().__init__(_printer(spacer))


def _suppress(x):
    return False


class Suppress(Filter):
    def __init__(self):
        super().__init__(_suppress)
