"""
Test database building.

"""
from io import StringIO
from tempfile import NamedTemporaryFile

from hamcrest import (
    assert_that,
    equal_to,
)
from microcosm.api import create_object_graph
from microcosm.loaders import load_from_dict

from microcosm_sqlite.tests.fixtures import (
    Example,
    Person,
    PersonStore,
)


class TestCSVDumpers:

    def setup(self):
        self.tmp_file = NamedTemporaryFile()
        loader = load_from_dict(
            sqlite=dict(
                paths=dict(
                    example=self.tmp_file.name,
                ),
            ),
        )
        self.graph = create_object_graph("example", testing=True, loader=loader)
        self.dumper = self.graph.sqlite_dumper

        self.person_store = PersonStore()

        Example.create_all(self.graph)

        self.outfile = StringIO()
        with Example.new_context(self.graph):
            self.person_store.create(
                Person(
                    id="1",
                    first="Stephen",
                    last="Curry",
                )
            )
            self.person_store.create(
                Person(
                    id="2",
                    first="Klay",
                    last="Thompson",
                )
            )
            self.person_store.session.commit()
        self.context = Person.new_context(self.graph).open()

    def teardown(self):
        self.tmp_file.close()

    def test_dump_with_csv_dump(self):
        self.dumper.csv(self.person_store).dump(
            self.outfile,
            field_names=["id", "first", "last"],
        )
        assert_that(
            self.outfile.getvalue(),
            equal_to("id,first,last\r\n1,Stephen,Curry\r\n2,Klay,Thompson\r\n")
        )

    def test_dump_selected_portion(self):
        self.dumper.csv(self.person_store).dump(
            self.outfile,
            items=self.person_store.search(first="Klay"),
            field_names=["id", "first", "last"],
        )
        assert_that(
            self.outfile.getvalue(),
            equal_to("id,first,last\r\n2,Klay,Thompson\r\n")
        )
