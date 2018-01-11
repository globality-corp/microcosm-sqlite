"""
SQLite factories.

"""
from distutils.util import strtobool
from pkg_resources import iter_entry_points

from microcosm.api import defaults
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@defaults(
    echo="False",
    path=":memory:",
    paths=dict(),
)
class SQLiteBindFactory:
    """
    A factory for SQLite engines and sessionmakers based on a name.

    """
    def __init__(self, graph):
        self.default_echo = strtobool(graph.config.sqlite.echo)
        self.default_path = graph.config.sqlite.path

        self.engines = dict()
        self.sessionmakers = dict()
        self.paths = {
            entry_point.name: entry_point.load()()
            for entry_point in iter_entry_points("microcosm.sqlite")
        }
        self.paths.update(graph.config.sqlite.paths)

    def __getitem__(self, key):
        return self.paths[key]

    def __setitem__(self, key, value):
        self.paths[key] = value

    def __call__(self, name):
        """
        Return a configured engine and sessionmaker for the named sqlite database.

        Instances are cached on create and instantiated using configured paths.

        """
        if name not in self.engines:
            path = self.paths.get(name, self.default_path)

            engine = create_engine(f"sqlite:///{path}", echo=self.default_echo)
            Session = sessionmaker(bind=engine)
            self.engines[name] = engine
            self.sessionmakers[name] = Session

        return self.engines[name], self.sessionmakers[name]
