import collections
import concurrent.futures as cf
import os

import typing_extensions as tp

from .basics import Map
from .core import Operator

T = tp.TypeVar("T")
U = tp.TypeVar("U")

__all__ = ("PoolMap", "UnorderedPoolMap")


class PoolMap(Operator[T, U], tp.Generic[T, U]):
    """Operator that submits items to a cf.Executor for processing.

    The function for processing can be a simple callable or an Operator.
    If an Operator is used, it is suggested that Filters are excluded.
    """

    def __init__(
        self,
        func: tp.Union[tp.Callable[[T], U], Operator[T, U]],
        *,
        pool_size: tp.Optional[int] = None,
        executor_cls: type[cf.Executor] = cf.ProcessPoolExecutor,
    ) -> None:
        if isinstance(func, Operator):
            self.op = func
        elif callable(func):
            self.op = Map(func)

        self.pool_size = os.cpu_count() if pool_size is None else pool_size
        self.executor_cls = executor_cls

    def pipe(self, iterable: tp.Iterable[T]) -> tp.Generator[U, None, None]:
        executor = self.executor_cls(max_workers=self.pool_size)
        try:
            self._handle(iterable, executor=executor)
        except GeneratorExit:
            # If we get an explicit .close() call, don't wait for existing futures to complete.
            executor.shutdown(wait=False)
        finally:
            executor.shutdown(wait=True)

    def _handle(self, iterable, executor):
        # After we submit a job, we'll store the future in the queue and the `not_done` set.
        # If the not_done set is ever too small, we'll fill it up to maximize pool occupancy.
        # If the not_done set is full, then we wait for the first future to complete.
        # The remaining futures are used to prepopulate the `not_done` set for the next iteration.
        # We yield the elements in submission order.
        queue: collections.deque[cf.Future[U]] = collections.deque()
        not_done: set[cf.Future[U]] = set()
        for elem in iterable:
            fut = executor.submit(self.op.send, elem)
            queue.append(fut)
            not_done.add(fut)
            if len(not_done) < self.pool_size:
                # Keep the pool full!
                continue

            _done, not_done = cf.wait(not_done, return_when=cf.FIRST_COMPLETED)
            while queue and queue[0].done():
                yield queue.popleft().result()

        # If we exhaust the source iterable, make to sure to yield the remaining elements.
        for fut in queue:
            yield fut.result()


class UnorderedPoolMap(PoolMap[T, U], tp.Generic[T, U]):
    """A PoolMap-varients where items are not necessarily yielded in iteration order.

    For tasks where the order of yielded elements is not critical, this can be slightly
    lower latency than the default PoolMap.
    """

    def _handle(self, iterable, executor):
        not_done: set[cf.Future[U]] = set()
        for elem in iterable:
            not_done.add(executor.submit(self.op.send, elem))

            if len(not_done) < self.pool_size:
                # Keep the pool full!
                continue

            done, not_done = cf.wait(not_done, return_when=cf.FIRST_COMPLETED)

            for fut in done:
                yield fut.result()

        for completed_fut in cf.as_completed(not_done):
            yield completed_fut.result()
