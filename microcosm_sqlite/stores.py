"""
Persistence abstractions.

"""
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from threading import local
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from microcosm_sqlite.errors import (
    DuplicateModelError,
    ModelIntegrityError,
    ModelNotFoundError,
    MultipleModelsFoundError,
)


def get_session(store):
    """
    Return the current session or raise an error.

    """
    data_set = store.model_class.resolve()
    session = data_set.session
    if session is None:
        raise AttributeError("No session is available in SQLiteContext")

    return session


class GetOrCreateSession:

    def __init__(self, graph, expire_on_commit=False):
        graph.use("sqlite")
        self.graph = graph
        self.expire_on_commit = expire_on_commit

    def __call__(self, store):
        """
        Return the current session or create a new one.

        """
        data_set = store.model_class.resolve()

        # support context access
        try:
            session = data_set.session
        except AttributeError:
            session = None

        if session is not None:
            return session

        # support thread local access
        try:
            thread_local = data_set.local
        except AttributeError:
            thread_local = data_set.local = local()

        try:
            session = thread_local.session
        except AttributeError:
            pass

        if session is None:
            session = data_set.new_session(
                graph=self.graph,
                expire_on_commit=self.expire_on_commit,
            )
            thread_local.session = session

        return session


class Store(metaclass=ABCMeta):
    """
    A persistence layer for SQLite-backed models.

    """
    auto_filter_fields: Optional[list] = None

    def __init__(self, get_session=get_session):
        self.get_session = get_session
        self.auto_filters = {
            auto_filter_field.name: auto_filter_field
            for auto_filter_field in (
                self.auto_filter_fields or []
            )
        }

    @property
    @abstractmethod
    def model_class(self):
        """
        The model class instance.

        """
        pass

    def count(self, **kwargs):
        """
        Count the number of models matching some criterion.

        """
        query = self._query()
        query = self._filter(query, **kwargs)
        return query.count()

    def create(self, instance):
        """
        Create a new model instance.

        """
        with self.flushing():
            self.session.add(instance)
        return instance

    def delete(self, **kwargs):
        """
        Delete a model or raise an error if not found.

        """
        query = self._query()
        query = self._filter(query, **kwargs)

        with self.flushing():
            count = query.delete()

        if count == 0:
            raise ModelNotFoundError

        return True

    def first(self, offset=None, limit=None, **kwargs):
        """
        Returns the first match based on criteria or None.

        :param offset: pagination offset, if any
        :param limit: pagination limit, if any

        """
        # Note that the ordering here is important.  In order to produce valid
        # SQL, _order_by must occur before _paginate, and _filter must occur
        # before _order_by.
        query = self._query()
        query = self._filter(query, **kwargs)
        query = self._order_by(query, **kwargs)
        query = self._paginate(query, offset=offset, limit=limit)
        return query.first()

    def one(self, offset=None, limit=None, **kwargs):
        """
        Returns a single match or raise an error.

        :param offset: pagination offset, if any
        :param limit: pagination limit, if any

        """
        # Note that the ordering here is important.  In order to produce valid
        # SQL, _order_by must occur before _paginate, and _filter must occur
        # before _order_by.
        query = self._query()
        query = self._filter(query, **kwargs)
        query = self._order_by(query, **kwargs)
        query = self._paginate(query, offset=offset, limit=limit)
        try:
            return query.one()
        except NoResultFound as error:
            raise ModelNotFoundError(error)
        except MultipleResultsFound as error:
            raise MultipleModelsFoundError(error)

    def search(self, offset=None, limit=None, **kwargs):
        """
        Return the list of models matching some criterion.

        :param offset: pagination offset, if any
        :param limit: pagination limit, if any

        """
        # Note that the ordering here is important.  In order to produce valid
        # SQL, _order_by must occur before _paginate, and _filter must occur
        # before _order_by.
        query = self._query()
        query = self._filter(query, **kwargs)
        query = self._order_by(query, **kwargs)
        query = self._paginate(query, offset=offset, limit=limit)

        return query.all()

    def _query(self):
        """
        Construct a query for the model.

        """
        return self.session.query(
            self.model_class,
        )

    def _filter(self, query, **kwargs):
        """
        Filter a query with user-supplied arguments.

        By default, it is a noop.  Derived classes can override this method to
        add filters or except clauses to the query.

        """
        query = self._auto_filter(query, **kwargs)
        return query

    def _auto_filter(self, query, **kwargs):
        for key, value in kwargs.items():
            if value is None:
                continue
            field = self.auto_filters.get(key)
            if field is None:
                continue
            query = query.filter(field == value)

        return query

    def _order_by(self, query, **kwargs):
        """
        Add an order by clause to a (search) query.

        By default, is a noop.

        """
        return query

    def _paginate(self, query, offset=None, limit=None):
        """
        Handle limit and offset.

        :param offset: pagination offset, if any
        :param limit: pagination limit, if any

        """

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return query

    @property
    def session(self):
        return self.get_session(self)

    @contextmanager
    def flushing(self):
        """
        Flush the current session (at the end of context).

        """
        try:
            yield
            self.session.flush()
        except IntegrityError as error:
            self.session.rollback()

            if "UNIQUE constraint failed" in str(error):
                raise DuplicateModelError(error)
            raise ModelIntegrityError(error)
