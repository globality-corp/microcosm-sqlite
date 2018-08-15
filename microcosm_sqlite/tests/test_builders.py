"""
Test database building.

"""
from io import StringIO
from tempfile import NamedTemporaryFile
from textwrap import dedent

from hamcrest import (
    assert_that,
    contains,
    has_properties,
    equal_to,
    is_,
)
from microcosm.api import create_object_graph
from microcosm.loaders import load_from_dict

from microcosm_sqlite.tests.fixtures import (
    Dog,
    DogStore,
    Example,
    Person,
    PersonStore,
)


def csv(s):
    return StringIO(s.strip())


class TestCSVBuilders:

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
        self.builder = self.graph.sqlite_builder

        self.dog_store = DogStore()
        self.person_store = PersonStore()

        Example.create_all(self.graph)

        self.people = csv(dedent("""
            id,first,last
             1,Stephen,Curry
             2,Klay,Thompson
        """))

        self.dogs = csv(dedent("""
            id,name,owner_id
             1,Rocco,2
             2,Reza,1
             3,Rookie,1
        """))

    def teardown(self):
        self.tmp_file.close()

    def test_build_with_csv_builder(self):
        self.builder.csv(Person).build(self.people)
        self.builder.csv(Dog).build(self.dogs)

        with Example.new_context(self.graph):
            dogs = self.dog_store.search()
            people = self.person_store.search()

            assert_that(
                dogs,
                contains(
                    has_properties(
                        name="Reza",
                    ),
                    has_properties(
                        name="Rocco",
                    ),
                    has_properties(
                        name="Rookie",
                    ),
                ),
            )
            assert_that(
                people,
                contains(
                    has_properties(
                        first="Klay",
                    ),
                    has_properties(
                        first="Stephen",
                    ),
                ),
            )

            for dog in dogs:
                assert_that(dog.is_a_good_boy, is_(equal_to(True)))

            assert_that(dogs[0].owner, is_(equal_to(people[1])))

    def test_build_with_bulk_csv_builder(self):
        bulk_input = [
            (Person, self.people),
            (Dog, self.dogs),
        ]

        self.builder.csv(Example).bulk().build(bulk_input)

        with Example.new_context(self.graph):
            dogs = self.dog_store.search()
            people = self.person_store.search()

            assert_that(
                dogs,
                contains(
                    has_properties(
                        name="Reza",
                    ),
                    has_properties(
                        name="Rocco",
                    ),
                    has_properties(
                        name="Rookie",
                    ),
                ),
            )

            assert_that(
                people,
                contains(
                    has_properties(
                        first="Klay",
                    ),
                    has_properties(
                        first="Stephen",
                    ),
                ),
            )

    def test_bulk_builder_when_violating_foreign_keys(self):
        dogs = csv(dedent("""
            id,name,owner_id
             1,Rocco,2
             2,Reza,1
             3,Rookie,1
             4,Stretch,3
        """))

        more_people = csv(dedent("""
            id,first,last
             3,John,Doe
        """))

        bulk_input = [
            (Person, self.people),
            (Dog, dogs),
            (Person, more_people),
        ]

        self.builder.csv(Example).bulk().build(bulk_input)

        with Example.new_context(self.graph):
            dogs = self.dog_store.search()
            people = self.person_store.search()

            assert_that(
                dogs,
                contains(
                    has_properties(
                        name="Reza",
                    ),
                    has_properties(
                        name="Rocco",
                    ),
                    has_properties(
                        name="Rookie",
                    ),
                    has_properties(
                        name="Stretch",
                    ),
                ),
            )

            assert_that(
                people,
                contains(
                    has_properties(
                        first="John",
                    ),
                    has_properties(
                        first="Klay",
                    ),
                    has_properties(
                        first="Stephen",
                    ),
                ),
            )

    def test_build_with_csv_builder_default(self):
        """
        Known values can be defaulted (for entire CSVs)

        """
        people = csv(dedent("""
            id,first
             1,Stephen
             2,Dell
        """))
        self.builder.csv(Person).default(last="Curry").build(people)
