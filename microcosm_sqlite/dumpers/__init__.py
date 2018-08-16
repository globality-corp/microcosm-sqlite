"""
Dump SQLite databases to file.

"""
from microcosm_sqlite.dumpers.csv import CSVDumper


class SQLiteDumper:
    """
    Top-level binding for SQLite database building.

    """
    def __init__(self, graph):
        self.graph = graph

    def csv(self, store, **kwargs):
        return CSVDumper(self.graph, store, **kwargs)
