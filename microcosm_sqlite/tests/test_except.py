from tempfile import NamedTemporaryFile

from hamcrest import assert_that, contains
from microcosm.api import create_object_graph
from microcosm.loaders import load_from_dict

from microcosm_sqlite.context import SessionContext
from microcosm_sqlite.tests.fixtures import Example, Person, PersonExclusionStore


def test_except():
    with NamedTemporaryFile() as tmp_file:
        # NB: not using :memory: sqlite database
        # as it maintains single database connection
        loader = load_from_dict(
            sqlite=dict(
                paths=dict(
                    example=tmp_file.name,
                ),
            ),
        )
        graph = create_object_graph("example", testing=True, loader=loader)
        store = PersonExclusionStore()

        Person.recreate_all(graph)

        person1 = Person(
            id=1,
            first="John",
            last="Krakow",
        )

        person2 = Person(
            id=2,
            first="Susan",
            last="Krakow",
        )

        with SessionContext(graph, Example):
            store.create(person1)
            store.create(person2)

            assert_that(
                store.search(
                    last="Krakow",
                    exclude_first="John",
                    limit=5,
                ),
                contains(person2),
            )
