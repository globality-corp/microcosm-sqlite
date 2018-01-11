"""
Test fixture.

"""
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from microcosm_sqlite import DataSet, Store
from microcosm_sqlite.models import IdentityMixin


Example = DataSet.create("example")


class Person(IdentityMixin, Example):
    __tablename__ = "person"

    id = Column(Integer, primary_key=True)
    first = Column(String, nullable=False)
    last = Column(String, nullable=False)

    @property
    def identity(self):
        return self.id

    __table_args__ = (
        Index(
            "unique_name",
            first,
            last,
            unique=True,
        ),
    )


class Dog(IdentityMixin, Example):
    __tablename__ = "dog"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    is_a_good_boy = Column(Boolean, nullable=False, default=True)
    owner_id = Column(Integer, ForeignKey(Person.id), nullable=False)
    owner = relationship(Person)

    @property
    def identity(self):
        return self.id


class PersonStore(Store):

    @property
    def model_class(self):
        return Person

    def _filter(self, query, first=None, last=None, **kwargs):
        if first is not None:
            query = query.filter(
                Person.first == first,
            )

        if last is not None:
            query = query.filter(
                Person.last == last,
            )

        return super()._filter(query, **kwargs)

    def _order_by(self, query, **kwargs):
        return query.order_by(
            Person.first.asc(),
            Person.last.asc(),
        )


class DogStore(Store):

    @property
    def model_class(self):
        return Dog

    def _order_by(self, query, **kwargs):
        return query.order_by(
            Dog.name.asc(),
        )
