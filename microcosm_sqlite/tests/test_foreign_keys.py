from tempfile import NamedTemporaryFile

from hamcrest import assert_that, calling, raises
from microcosm.api import create_object_graph
from microcosm.loaders import load_from_dict

from microcosm_sqlite.context import SessionContext
from microcosm_sqlite.errors import ModelIntegrityError
from microcosm_sqlite.tests.fixtures import Dog, DogStore, Example


def test_foreign_keys():
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
        store = DogStore()

        Dog.recreate_all(graph)

        dog = Dog(
            id=1,
            name="Hooch",
            owner_id=999,
        )

        with SessionContext(graph, Example):
            assert_that(
                calling(store.create).with_args(dog),
                raises(ModelIntegrityError),
            )
