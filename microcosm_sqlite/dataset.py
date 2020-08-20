"""
Abstraction around a SQLite-based data set.

"""
from inspect import getmro

from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

from microcosm_sqlite.constants import naming_convention
from microcosm_sqlite.context import SessionContext


class DataSet:
    """
    A base class for a declarative base, representing a set of related types.

    All derived types will use the same engine and session maker.

    """
    @staticmethod
    def create(name, cls=None, **kwargs):
        """
        Create a new declarative base class.

        Because applications are likely to use multiple SQLite databases at once,
        every declarative base class is expected to use a unique base class, which is
        used to identity the correct engine and sessionmaker in the BindFactory.

        Note that we use `naming_convention` to ensure that all of our
        constraints automatically get names if one is not provided.  Otherwise
        Alembic migrations will fail.  See https://alembic.sqlalchemy.org/en/latest/naming.html

        """
        return declarative_base(
            name=name,
            cls=DataSet,
            metadata=MetaData(naming_convention=naming_convention),
            **kwargs,
        )

    @classmethod
    def resolve(cls):
        """
        Resolve the derived declarative base.

        """
        for base in getmro(cls):
            if DataSet in base.__bases__:
                return base

        raise Exception(f"Not a valid DataSet: {cls}")

    @classmethod
    def create_all(cls, graph):
        """
        Create schemas for all declared types of this data set.

        If multiple types are declared for the same declarative base class, all related
        schemas will be created.

        """
        name = cls.resolve().__name__
        engine, _ = graph.sqlite(name)
        cls.metadata.create_all(bind=engine)

    @classmethod
    def drop_all(cls, graph):
        """
        Drop schemas for all declared types of this data set.

        If multiple types are declared for the same declarative base class, all related
        schemas will be created.

        """
        name = cls.resolve().__name__
        engine, _ = graph.sqlite(name)
        cls.metadata.drop_all(bind=engine)

    @classmethod
    def recreate_all(cls, graph):
        """
        Drop and recreate schemas.

        """
        cls.drop_all(graph)
        cls.create_all(graph)

    @classmethod
    def new_session(cls, graph, **kwargs):
        """
        Create a new session.

        """
        name = cls.resolve().__name__
        _, Session = graph.sqlite(name)
        return Session(**kwargs)

    @classmethod
    def new_context(cls, graph, **kwargs):
        """
        Create a new session context.

        """
        return SessionContext(
            graph=graph,
            data_set=cls.resolve(),
            **kwargs
        )

    @classmethod
    def dispose(cls, graph):
        """
        Dispose of an entire engine.

        """
        name = cls.resolve().__name__
        engine, _ = graph.sqlite(name)
        engine.dispose()


def dispose_sqlite_connections(graph):
    """
    Dispose all SQLite connections, SQLAlchemy engine and
    thread-local references to session.

    Meant to be called on post-fork, to make sure we use
    new DB connections in child processes.

    Docs:
      - https://docs.sqlalchemy.org/en/13/core/connections.html#engine-disposal
      - https://www.sqlite.org/howtocorrupt.html (section 2.6)

    """
    for data_set in DataSet.__subclasses__():
        # NB closing session in case it's open.
        session = getattr(data_set, "session", None)
        if session is not None:
            session.close()

        data_set.session = None

        # NB cleanup thread-local session container (initialized in
        # microcosm_sqlite.stores.GetOrCreateSession), to make sure
        # we initialize new one in the child process.
        try:
            del data_set.local
        except AttributeError:
            pass

        data_set.dispose(graph)
