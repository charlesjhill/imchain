import pytest

import imchain.operator as iop


def test_pipe():
    for x, y in zip(iop.Noop().pipe(range(3)), range(3)):
        assert x == y


def test_pipe_is_lazy():
    it = iter(range(3))
    git = iop.Noop().pipe(it)

    assert next(git) == 0
    assert next(it) == 1
    assert next(git) == 2


def test_drain():
    it = iter(range(3))
    ret = iop.Noop().drain(it)

    assert ret is None
    with pytest.raises(StopIteration):
        next(it)


def test_process():
    it = iter(range(3))
    ret = iop.Noop().process(it)
    assert ret == list(range(3))
    with pytest.raises(StopIteration):
        next(it)


def test_send():
    assert iop.Noop().send(0) == 0
    assert iop.Noop().send([5]) == [5]

    adder = iop.Map(lambda x: x + 1)
    duper = iop.Map(lambda x: (x, x))
    chain = duper | iop.Chain()

    assert adder.send(1) == 2
    assert duper.send(1) == (1, 1)
    assert chain.send(1) == (1, 1)


def test_to_tuple():
    adder = iop.Map(lambda x: x + 1)
    duper = iop.Map(lambda x: (x, x))
    chain = duper | iop.Chain()

    assert adder.send_to_tuple(1) == (2,)
    assert duper.send_to_tuple(1) == ((1, 1),)
    assert chain.send_to_tuple(1) == (1, 1)


def test_send_one_to_many():
    class DoubleYield(iop.Operator):
        def pipe(self, iterable):
            for item in iterable:
                yield item
                yield item

    yielder = DoubleYield()
    assert yielder.send(0) == (0, 0)


def test_chaining():
    op1 = iop.Map(lambda x: x + 1)
    op2 = iop.Map(lambda x: 2 * x)

    # Doesn't error out.
    chained = op1 | op2

    # Chaining creates a pipeline
    assert isinstance(chained, iop.Pipeline)
    # It applies one then two.
    assert chained.send(1) == 4

    # It doesn't create copies of the component operators.
    assert chained.operators[0] is op1
    assert chained.operators[1] is op2


def test_chain_3():
    op1 = iop.Map(lambda x: x + 1)
    op2 = iop.Map(lambda x: 2 * x)
    op3 = iop.Map(lambda x: x + 10)
    op4 = iop.Map(lambda x: 3 * x)

    chained = op1 | op2 | op3
    assert isinstance(chained, iop.Pipeline)
    assert len(chained) == 3
    orig_id = id(chained)

    chained |= op4
    assert len(chained) == 4
    assert id(chained) == orig_id

    assert chained.send(1) == (((1 + 1) * 2) + 10) * 3
