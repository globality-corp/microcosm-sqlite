from tempfile import NamedTemporaryFile
from typing import Any
from unittest.mock import patch

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    is_,
)
from microcosm.api import create_object_graph
from microcosm.loaders import load_from_dict
from sqlalchemy import Column, ForeignKey, Integer

from microcosm_sqlite import DataSet, Store, dispose_sqlite_connections


Base: Any = DataSet.create("example")
Base2: Any = DataSet.create("example_2")


class Foo(Base):
    __tablename__ = "foo"

    id = Column(Integer, primary_key=True)


class Bar(Foo):
    __tablename__ = "bar"

    id = Column(Integer, ForeignKey("foo.id"), primary_key=True)


class Baz(Bar):
    __tablename__ = "baz"

    id = Column(Integer, ForeignKey("bar.id"), primary_key=True)


class Foo2(Base2):
    __tablename__ = "foo_2"

    id = Column(Integer, primary_key=True)


class FooStore(Store):
    model_class = Foo


def test_resolve():
    assert_that(Foo.resolve(), is_(equal_to(Base)))
    assert_that(Bar.resolve(), is_(equal_to(Base)))
    assert_that(Baz.resolve(), is_(equal_to(Base)))


class TestDisposeSQLiteConnections:

    def setup_method(self):
        self.example_tmp_file = NamedTemporaryFile()
        loader = load_from_dict(
            sqlite=dict(
                paths=dict(
                    # NB using a file instead of ':memory:' path
                    # to preserve data after SQLAlchemy engine disposal.
                    example=self.example_tmp_file.name,
                ),
            ),
        )
        self.graph = create_object_graph(
            "example",
            testing=True,
            loader=loader,
        )
        self.foo_store = FooStore()
        self.foo = Foo(id=1)

        Foo.recreate_all(self.graph)
        Bar.recreate_all(self.graph)
        Baz.recreate_all(self.graph)
        Foo2.recreate_all(self.graph)

    def teardown(self):
        Foo.dispose(self.graph)
        Bar.dispose(self.graph)
        Baz.dispose(self.graph)
        Foo2.dispose(self.graph)

        self.example_tmp_file.close()

    def test_data_set_is_operational_after_disposal(self):
        dispose_sqlite_connections(self.graph)

        # NB after connection and SQLAlchemy engine
        # disposal, the objects should be re-initialized
        # on the next use.
        with Foo.new_context(self.graph).open() as context:
            self.foo_store.create(self.foo)
            context.commit()

            assert_that(self.foo_store.search(), contains(self.foo))

    def test_dispose_is_called_for_all_data_sets(self):
        with patch.object(Base, "dispose") as base_dispose:
            with patch.object(Base2, "dispose") as base_2_dispose:
                dispose_sqlite_connections(self.graph)

        base_2_dispose.assert_called_once()
        base_dispose.assert_called_once()

    def test_no_thread_local_container_and_session_after_disposal(self):
        with Foo.new_context(self.graph).open() as context:
            self.foo_store.create(self.foo)
            context.commit()

        dispose_sqlite_connections(self.graph)

        assert_that(hasattr(Base, "local"), is_(False))
        assert_that(hasattr(Base2, "local"), is_(False))
        assert_that(Base.session, is_(None))
        assert_that(Base2.session, is_(None))
