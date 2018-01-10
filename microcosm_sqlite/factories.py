"""
SQLite factories.

"""
from distutils.util import strtobool

from microcosm.api import defaults
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@defaults(
    path=":memory:",
    # echo all SQL
    echo="False",
)
def configure_sqlite_engine(graph):
    """
    Configure the SQLite engine for SQLAlchemy.

    The primary input is the connection URL path, which is assumed to have the form:

        sqlite:///{path}

    Note that valid SQLite URL forms are:

      sqlite:///:memory: (or, sqlite://)
      sqlite:///relative/path/to/file.db
      sqlite:////absolute/path/to/file.db

    """
    echo = strtobool(graph.config.sqlite.echo)
    path = graph.config.sqlite.path
    url = f"sqlite:///{path}"
    return create_engine(url, echo=echo)


def configure_sqlite_sessionmaker(graph):
    return sessionmaker(bind=graph.sqlite)
