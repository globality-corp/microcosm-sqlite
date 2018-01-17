"""
CSV-based building.

"""
from csv import DictReader


class CSVBuilder:
    """
    CSV-based builer for a single model class.

    """
    def __init__(self, graph, model_cls):
        self.graph = graph
        self.model_cls = model_cls
        self.columns = {
            column.name: (key, column)
            for key, column in model_cls.__mapper__.columns.items()
        }

    def build(self, fileobj):
        csv = DictReader(fileobj)

        with self.model_cls.new_context(self.graph) as context:
            for row in csv:
                model = self.as_model(row)
                context.session.add(model)
            context.commit()

    def as_model(self, row):
        return self.model_cls(**dict(
            self.as_tuple(name, value)
            for name, value in row.items()
            if name in self.columns
        ))

    def as_tuple(self, name, value):
        key, column = self.columns[name]
        if not value and column.nullable:
            return key, None
        return key, value
