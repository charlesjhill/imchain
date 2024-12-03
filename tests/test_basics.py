import imchain.operator as iop
import imchain.operator.util as iopu


def test_where_simple():
    op = iop.Where(lambda x: x % 2 == 0).then(lambda x: x // 2).otherwise(lambda x: 3 * x + 1)
    src = [0, 1, 2, 3]
    res = op.process(src)
    assert res == [0, 4, 1, 10]


def test_where_filters():
    op = iop.Where(lambda x: x % 2 == 0).then(iopu.Suppress()).otherwise(lambda x: x + 1)
    src = [0, 1, 2, 3]
    res = op.process(src)
    assert res == [2, 4]


def test_where_one_to_many():
    duper = iop.FlatMap(lambda x: (x, x))
    op = iop.Where(lambda x: x % 2 == 0).then(duper).otherwise(lambda x: x + 10)
    src = [0, 1, 2, 3]
    res = op.process(src)
    assert res == [0, 0, 11, 2, 2, 13]
