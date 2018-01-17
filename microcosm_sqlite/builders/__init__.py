"""
Build SQLite databases.

"""
from microcosm_sqlite.builders.csv import CSVBuilder


class SQLiteBuilder:
    """
    Top-level binding for SQLite database building.

    """
    def __init__(self, graph):
        self.graph = graph

    def csv(self, model_cls):
        return CSVBuilder(self.graph, model_cls)
