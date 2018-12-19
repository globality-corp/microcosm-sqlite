from hamcrest import assert_that, equal_to, is_
from sqlalchemy import Column, ForeignKey, Integer
from typing import Any

from microcosm_sqlite import DataSet


Base: Any = DataSet.create("example")


class Foo(Base):
    __tablename__ = 'foo'

    id = Column(Integer, primary_key=True)


class Bar(Foo):
    __tablename__ = 'bar'

    id = Column(Integer, ForeignKey('foo.id'), primary_key=True)


class Baz(Bar):
    __tablename__ = 'baz'

    id = Column(Integer, ForeignKey('bar.id'), primary_key=True)


def test_resolve():
    assert_that(Foo.resolve(), is_(equal_to(Base)))
    assert_that(Bar.resolve(), is_(equal_to(Base)))
    assert_that(Baz.resolve(), is_(equal_to(Base)))
