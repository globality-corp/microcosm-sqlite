"""
Abstraction around a SQLite-based data set.

"""
from inspect import getmro

from sqlalchemy.ext.declarative import declarative_base

from microcosm_sqlite.context import SessionContext


SESSION = "__session__"


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

        """
        return declarative_base(name=name, cls=DataSet, **kwargs)

    @classmethod
    def resolve(cls):
        """
        Resolve the derived declarative base.

        """
        for base in getmro(cls):
            if DataSet in base.__bases__:
                return base

        raise Exception(f"Not a valid DataSet: {cls}")

    @property
    def session(self):
        """
        Get the current session attached to this data set (if any)

        """
        return getattr(self.__class__.resolve(), SESSION, None)

    @session.setter
    def session(self, session):
        """
        Set the session attached to this data set.

        """
        setattr(self.__class__.resolve(), SESSION, session)

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
