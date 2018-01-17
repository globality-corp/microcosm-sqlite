"""
Test factory logic.

"""
from tempfile import NamedTemporaryFile

from hamcrest import (
    assert_that,
    calling,
    empty,
    equal_to,
    is_,
    is_not,
    raises,
)
from microcosm.api import create_object_graph
from microcosm.loaders import load_from_dict


class TestSQLiteBindFactory:

    def setup(self):
        self.tmp_file = NamedTemporaryFile()
        loader = load_from_dict(
            sqlite=dict(
                paths=dict(
                    foo=self.tmp_file.name,
                ),
            ),
        )
        self.graph = create_object_graph("example", testing=True, loader=loader)

    def teardown(self):
        self.tmp_file.close()

    def test_config(self):
        # no datasets initially
        assert_that(self.graph.sqlite.datasets, is_(empty()))
        # path configuration includes explicit config (and entry point config)
        assert_that(self.graph.sqlite.paths, is_(equal_to(dict(
            foo=self.tmp_file.name,
        ))))

    def test_getitem_and_setitem(self):
        assert_that(self.graph.sqlite["foo"], is_(equal_to(self.tmp_file.name)))
        assert_that(
            calling(self.graph.sqlite.__getitem__).with_args("bar"),
            raises(KeyError),
        )
        self.graph.sqlite["bar"] = ":memory:"
        assert_that(self.graph.sqlite["bar"], is_(equal_to(":memory:")))

    def test_call(self):
        foo_engine, FooSession = self.graph.sqlite("foo")
        assert_that(str(foo_engine.url), is_(equal_to(f"sqlite:///{self.tmp_file.name}")))
        assert_that(FooSession.kw["bind"], is_(equal_to(foo_engine)))

        bar_engine, BarSession = self.graph.sqlite("bar")
        assert_that(str(bar_engine.url), is_(equal_to(f"sqlite:///:memory:")))
        assert_that(BarSession.kw["bind"], is_(equal_to(bar_engine)))

        assert_that(foo_engine, is_not(equal_to(bar_engine)))
        assert_that(FooSession, is_not(equal_to(BarSession)))
