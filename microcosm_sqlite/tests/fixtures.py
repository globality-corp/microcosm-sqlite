"""
Test fixture.

"""
from typing import Any

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import select

from microcosm_sqlite import DataSet, Store
from microcosm_sqlite.models import IdentityMixin


Example: Any = DataSet.create("example")


class Person(IdentityMixin, Example):
    __tablename__ = "person"

    id = mapped_column(Integer, primary_key=True)
    first = mapped_column(String, nullable=False)
    last = mapped_column(String, nullable=False)

    @property
    def identity(self):
        return self.id

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.id}")'

    def __str__(self):
        return f'{self.first} {self.last}'

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

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, nullable=False)
    is_a_good_boy = mapped_column(Boolean, nullable=False, default=True)
    owner_id = mapped_column(Integer, ForeignKey(Person.id), nullable=False)
    owner = relationship(Person)

    @property
    def identity(self):
        return self.id


class PersonStore(Store):
    model_class = Person
    auto_filter_fields = [
        model_class.first,
    ]

    def _filter(self, query, last=None, **kwargs):
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


class PersonExclusionStore(PersonStore):
    def _except_clause_for(self, exclude_first):
        return select(Person).where(Person.first == exclude_first)

    def _filter(self, query, exclude_first=None, **kwargs):
        if exclude_first is not None:
            query = query.except_(
                self._except_clause_for(exclude_first=exclude_first)
            )

        return super()._filter(query, **kwargs)


class DogStore(Store):

    @property
    def model_class(self):
        return Dog

    def _order_by(self, query, **kwargs):
        return query.order_by(
            Dog.name.asc(),
        )
