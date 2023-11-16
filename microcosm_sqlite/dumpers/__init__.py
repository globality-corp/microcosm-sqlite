"""
Dump SQLite databases to file.

"""
from microcosm.api import binding

from microcosm_sqlite.dumpers.csv import CSVDumper


@binding("sqlite_dumper")
class SQLiteDumper:
    """
    Top-level binding for SQLite database building.

    """

    def __init__(self, graph):
        self.graph = graph

    def csv(self, store, **kwargs):
        return CSVDumper(self.graph, store, **kwargs)
