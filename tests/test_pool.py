import concurrent.futures as cf
import time

import pytest

import imchain.operator as iop
from imchain.operator import util as iopu


@pytest.mark.parametrize("exec_cls", [cf.ThreadPoolExecutor, cf.ProcessPoolExecutor])
@pytest.mark.parametrize("mapper_cls", [iop.PoolMap, iop.UnorderedPoolMap])
def test_poolmap(exec_cls, mapper_cls):
    pool_op = iopu.Wait(0.1)
    chain = mapper_cls(pool_op, pool_size=3, executor_cls=exec_cls)

    start = time.perf_counter()
    chain.drain(range(6))
    delta = time.perf_counter() - start

    # This should take ~0.2s if the pool works.
    assert delta < 0.3


@pytest.mark.parametrize("exec_cls", [cf.ThreadPoolExecutor, cf.ProcessPoolExecutor])
def test_ordered_poolmap(exec_cls):
    inp = [0, 0.05, 0.1]
    pool_op = iopu.WaitData(inverse_time=0.1)

    # The PoolMap orders the results.
    chain = iop.PoolMap(pool_op, pool_size=3, executor_cls=exec_cls)
    res = chain.process(inp)
    assert res == inp

    # Unordered does not!
    chain = iop.UnorderedPoolMap(pool_op, pool_size=3, executor_cls=exec_cls)
    res = chain.process(inp)
    assert res == inp[::-1]
