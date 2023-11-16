"""
Build SQLite databases.

"""
from microcosm.api import binding

from microcosm_sqlite.builders.csv import CSVBuilder


@binding("sqlite_builder")
class SQLiteBuilder:
    """
    Top-level binding for SQLite database building.

    """
    def __init__(self, graph):
        self.graph = graph

    def csv(self, model_cls, **kwargs):
        return CSVBuilder(self.graph, model_cls, **kwargs)
