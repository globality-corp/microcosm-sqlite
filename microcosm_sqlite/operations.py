"""
"""
from microcosm_sqlite.models import Base


def create_all(graph):
    """
    Create all database tables.

    """
    Base.metadata.create_all(graph.sqlite)


def drop_all(graph):
    """
    Drop all database tables.

    """
    Base.metadata.drop_all(graph.sqlite)


def recreate_all(graph):
    """
    Drop and add back all database tables.

    """
    drop_all(graph)
    create_all(graph)


def new_session(graph, expire_on_commit=False):
    return graph.sqlite_sessionmaker(
        expire_on_commit=expire_on_commit,
    )
