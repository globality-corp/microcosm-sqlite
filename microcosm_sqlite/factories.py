"""
SQLite factories.

"""
from distutils.util import strtobool
from pkg_resources import iter_entry_points

from microcosm.api import defaults
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


def on_connect_listener(use_foreign_keys):
    def enforce_foreign_keys(connection, _):
        if use_foreign_keys:
            connection.execute("PRAGMA foreign_keys=ON")

    return enforce_foreign_keys


@defaults(
    echo="False",
    path=":memory:",
    paths=dict(),
    use_foreign_keys="True",
)
class SQLiteBindFactory:
    """
    A factory for SQLite engines and sessionmakers based on a name.

    """
    def __init__(self, graph):
        self.default_path = graph.config.sqlite.path
        self.echo = strtobool(graph.config.sqlite.echo)
        self.use_foreign_keys = strtobool(graph.config.sqlite.use_foreign_keys)

        self.datasets = dict()
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
        if name not in self.datasets:
            path = self.paths.get(name, self.default_path)
            engine = create_engine(f"sqlite:///{path}", echo=self.echo)
            event.listen(engine, "connect", on_connect_listener(self.use_foreign_keys))

            Session = sessionmaker(bind=engine)

            self.datasets[name] = engine, Session

        return self.datasets[name]
