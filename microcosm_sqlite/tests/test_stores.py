"""
Test stores with fixtures.

"""
from hamcrest import (
    assert_that,
    calling,
    contains,
    equal_to,
    empty,
    is_,
    none,
    raises,
)
from microcosm.api import create_object_graph

from microcosm_sqlite.errors import (
    DuplicateModelError,
    ModelIntegrityError,
    ModelNotFoundError,
    MultipleModelsFoundError,
)
from microcosm_sqlite.tests.fixtures import Person, PersonStore


class TestStore:

    def setup(self):
        self.graph = create_object_graph("example", testing=True)

        self.gw = Person(id=1, first="George", last="Washington")
        self.tj = Person(id=2, first="Thomas", last="Jefferson")
        self.store = PersonStore()

        Person.recreate_all(self.graph)
        self.context = Person.new_context(self.graph).open()

    def populate(self):
        self.store.create(self.tj)
        self.store.create(self.gw)
        self.context.commit()

    def teardown(self):
        self.context.close()
        Person.dispose(self.graph)

    def test_count(self):
        assert_that(self.store.count(), is_(equal_to(0)))

        self.populate()

        assert_that(self.store.count(), is_(equal_to(2)))

    def test_create_integrity_error(self):
        assert_that(
            calling(self.store.create).with_args(Person(id=3, first=None, last=None)),
            raises(ModelIntegrityError),
        )

    def test_create_duplicate_error(self):
        self.store.create(Person(id=3, first="First", last="Last"))
        self.context.commit()

        assert_that(
            calling(self.store.create).with_args(Person(id=3, first="First", last="Last")),
            raises(DuplicateModelError),
        )

    def test_delete(self):
        self.populate()

        assert_that(
            self.store.delete(first=self.gw.first, last=self.gw.last),
            is_(equal_to(True)),
        )
        assert_that(
            calling(self.store.delete).with_args(first=self.gw.first, last=self.gw.last),
            raises(ModelNotFoundError),
        )

        assert_that(self.store.count(), is_(equal_to(1)))

    def test_first(self):
        assert_that(self.store.first(), is_(none()))

        self.populate()

        assert_that(self.store.first(), is_(equal_to(self.gw)))

    def test_one(self):
        assert_that(
            calling(self.store.one),
            raises(ModelNotFoundError),
        )

        self.populate()

        assert_that(
            calling(self.store.one),
            raises(MultipleModelsFoundError),
        )

        assert_that(self.store.one(limit=1), is_(equal_to(self.gw)))

    def test_search(self):
        assert_that(self.store.search(), is_(empty()))

        self.populate()

        assert_that(self.store.search(), contains(self.gw, self.tj))
