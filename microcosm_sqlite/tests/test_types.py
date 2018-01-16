"""
Test type conversion.

"""
from hamcrest import assert_that, equal_to, is_
from microcosm.api import create_object_graph
from sqlalchemy import Column, Integer

from microcosm_sqlite import DataSet
from microcosm_sqlite.models import IdentityMixin
from microcosm_sqlite.types import Truthy


Types = DataSet.create("types")


class Example(IdentityMixin, Types):
    __tablename__ = "example"

    id = Column(Integer, primary_key=True)
    value = Column(Truthy)


def test_truthy():
    CASES = [
        (True, True),
        (False, False),
        ("True", True),
        ("true", True),
        ("Yes", True),
        ("yes", True),
        ("No", False),
        ("no", False),
        (1, True),
        ("1", True),
        (0, False),
        ("", False),
        ("0", False),
    ]

    graph = create_object_graph("example")

    Types.create_all(graph)

    with Types.new_context(graph) as context:
        for index, (value, _) in enumerate(CASES):
            example = Example(id=index, value=value)
            context.session.add(example)
        context.commit()

    with Types.new_context(graph) as context:
        for index, (_, expected) in enumerate(CASES):
            example = context.session.query(Example).filter(Example.id == index).one()
            assert_that(example.value, is_(equal_to(expected)))
