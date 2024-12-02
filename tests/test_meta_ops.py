
import imchain.operator as iop


def test_buffer():
    source = list(range(5))
    bufferer = iop.Buffer(2)

    res = bufferer.process(source)
    assert res == [(0, 1), (2, 3), (4,)]


def test_buffer_drop_last():
    source = list(range(5))
    bufferer = iop.Buffer(2, drop_last=True)

    res = bufferer.process(source)
    assert res == [(0, 1), (2, 3)]


def test_chain():
    source = [(0, 1), (2, 3)]
    chained = iop.Chain()

    res = chained.process(source)
    assert res == [0, 1, 2, 3]


    source = [(0, 1), ((2, 3), (4, 5))]
    res = chained.process(source)
    assert res == [0, 1, (2, 3), (4, 5)]


def test_flatmap():
    op = iop.FlatMap(lambda x: (x, x))
    assert op.process(range(3)) == [0, 0, 1, 1, 2, 2]
