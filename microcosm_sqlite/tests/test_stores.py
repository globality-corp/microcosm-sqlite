"""
Test stores with fixtures.

"""
from microcosm.api import create_object_graph

from hamcrest import (
    assert_that,
    calling,
    contains,
    empty,
    equal_to,
    is_,
    none,
    raises,
)
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

        self.gc = Person(id=1, first="George", last="Clinton")
        self.gw = Person(id=2, first="George", last="Washington")
        self.rf = Person(id=3, first="Rosalind", last="Franklin")
        self.store = PersonStore()

        Person.recreate_all(self.graph)
        self.context = Person.new_context(self.graph).open()

    def populate(self):
        self.store.create(self.gw)
        self.store.create(self.rf)
        self.store.create(self.gc)
        self.context.commit()

    def teardown(self):
        self.context.close()
        Person.dispose(self.graph)

    def test_create_integrity_error(self):
        assert_that(
            calling(self.store.create).with_args(Person(id=3, first=None, last=None)),
            raises(ModelIntegrityError),
        )

    def test_create_after_integrity_error(self):
        assert_that(
            calling(self.store.create).with_args(Person(id=3, first=None, last=None)),
            raises(ModelIntegrityError),
        )

        # create works after IntegrityError
        self.store.create(self.gw)
        assert_that(self.store.search(), contains(self.gw))

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

        assert_that(self.store.count(), is_(equal_to(2)))

        self.store.delete()

        assert_that(self.store.count(), is_(equal_to(0)))

    def test_count(self):
        assert_that(self.store.count(), is_(equal_to(0)))

        self.populate()

        assert_that(self.store.count(), is_(equal_to(3)))
        # pagination arguments are not supported for count and should be ignored
        # if passed in
        assert_that(self.store.count(offset=1), is_(equal_to(3)))
        assert_that(self.store.count(limit=1), is_(equal_to(3)))
        assert_that(self.store.count(offset=1, limit=1), is_(equal_to(3)))

    def test_first(self):
        assert_that(self.store.first(), is_(none()))

        self.populate()

        assert_that(self.store.first(), is_(equal_to(self.gc)))
        assert_that(self.store.first(offset=1), is_(equal_to(self.gw)))
        assert_that(self.store.first(limit=1), is_(equal_to(self.gc)))
        assert_that(self.store.first(offset=1, limit=1), is_(equal_to(self.gw)))

    def test_one(self):
        assert_that(  # type: ignore
            calling(self.store.one),
            raises(ModelNotFoundError),
        )

        self.populate()

        assert_that(  # type: ignore
            calling(self.store.one),
            raises(MultipleModelsFoundError),
        )

        assert_that(
            calling(self.store.one).with_args(first="George"),
            raises(MultipleModelsFoundError),
        )

        assert_that(self.store.one(first="Rosalind"), is_(equal_to(self.rf)))
        assert_that(self.store.one(limit=1), is_(equal_to(self.gc)))
        assert_that(
            self.store.one(first="George", offset=1),
            is_(equal_to(self.gw))
        )
        assert_that(
            self.store.one(offset=1, limit=1),
            is_(equal_to(self.gw))
        )

    def test_search(self):
        assert_that(self.store.search(), is_(empty()))

        self.populate()

        assert_that(
            self.store.search(),
            contains(self.gc, self.gw, self.rf)
        )
        assert_that(
            self.store.search(offset=1),
            contains(self.gw, self.rf)
        )
        assert_that(
            self.store.search(limit=2),
            contains(self.gc, self.gw)
        )
        assert_that(
            self.store.search(offset=1, limit=1),
            contains(self.gw)
        )
