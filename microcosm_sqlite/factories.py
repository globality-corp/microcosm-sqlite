"""
SQLite factories.

"""
from distutils.util import strtobool
from pkg_resources import iter_entry_points

from microcosm.api import binding, defaults
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool


def on_connect_listener(use_foreign_keys):
    def on_connect(dbapi_connection, _):
        if use_foreign_keys:
            dbapi_connection.execute("PRAGMA foreign_keys=ON")

        # disable pysqlite's emitting of the BEGIN statement entirely,
        # also stops it from emitting COMMIT before any DDL
        # see: https://docs.sqlalchemy.org/en/latest/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl  # noqa
        dbapi_connection.isolation_level = None

    return on_connect


def on_begin_listener(connection):
    connection.execute(text("BEGIN"))


@binding("sqlite")
@defaults(
    echo="False",
    path=":memory:",
    paths=dict(),
    use_foreign_keys="True",
    read_only=False,
    poolclass=None,
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
            entry_point.name: entry_point.load()(graph)
            for entry_point in iter_entry_points("microcosm.sqlite")
        }
        self.paths.update(graph.config.sqlite.paths)
        self.read_only = graph.config.sqlite.read_only
        self.poolclass = graph.config.sqlite.poolclass or self._get_default_poolclass()

    def _get_default_poolclass(self):
        in_memory_db = self.default_path == ":memory:"
        return QueuePool if in_memory_db else NullPool

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
            engine = create_engine(
                f"sqlite:///{path}", poolclass=self.poolclass, echo=self.echo
            )

            event.listen(engine, "connect", on_connect_listener(self.use_foreign_keys))
            if not self.read_only:
                # We only need to use transactions if we're not in read_only mode
                event.listen(engine, "begin", on_begin_listener)

            Session = sessionmaker(bind=engine)

            self.datasets[name] = engine, Session

        return self.datasets[name]
