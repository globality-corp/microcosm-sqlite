"""
Test database building.

"""
from io import StringIO
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


class TestCSVBuilder:

    def setup(self):
        loader = load_from_dict(
            sqlite=dict(
                taxonomy=":memory:",
            ),
        )
        self.graph = create_object_graph("example", testing=True, loader=loader)
        self.builder = self.graph.sqlite_builder

        self.dog_store = DogStore()
        self.person_store = PersonStore()

        Example.create_all(self.graph)

    def test_build(self):
        people = csv(dedent("""
            id,first,last
             1,Stephen,Curry
             2,Klay,Thompson
        """))

        dogs = csv(dedent("""
            id,name,owner_id
             1,Rocco,2
             2,Reza,1
             3,Rookie,1
        """))

        self.builder.csv(Person).build(people)
        self.builder.csv(Dog).build(dogs)

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
