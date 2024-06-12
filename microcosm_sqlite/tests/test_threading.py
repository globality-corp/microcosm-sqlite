"""
Threading tests.

"""
from multiprocessing.pool import ThreadPool
from tempfile import NamedTemporaryFile

from hamcrest import assert_that, contains
from microcosm.api import create_object_graph
from microcosm.loaders import load_from_dict

from microcosm_sqlite.context import SessionContext
from microcosm_sqlite.stores import GetOrCreateSession
from microcosm_sqlite.tests.fixtures import Example, Person, PersonStore


def test_threading():
    with NamedTemporaryFile() as tmp_file:
        loader = load_from_dict(
            sqlite=dict(
                paths=dict(
                    example=tmp_file.name,
                ),
            ),
        )
        graph = create_object_graph("example", testing=True, loader=loader)
        store = PersonStore()

        Person.recreate_all(graph)

        with SessionContext(graph, Example) as context:
            gw = store.create(
                Person(id=1, first="George", last="Washington"),
            )
            tj = store.create(
                Person(id=2, first="Thomas", last="Jefferson"),
            )
            context.commit()

        pool = ThreadPool(2)

        store.get_session = GetOrCreateSession(graph)
        people = pool.map(lambda index: store.search()[index], range(2))

        assert_that(people, contains(gw, tj))
