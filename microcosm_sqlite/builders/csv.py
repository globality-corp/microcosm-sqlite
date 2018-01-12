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
        self.mapper = model_cls.__mapper__

    def build(self, fileobj):
        csv = DictReader(fileobj)

        with self.model_cls.new_context(self.graph) as context:
            for row in csv:
                model = self.as_model(row)
                context.session.add(model)
            context.commit()

    def as_model(self, row):
        return self.model_cls(**{
            key: self.as_value(key, value)
            for key, value in row.items()
        })

    def as_value(self, key, value):
        column = self.mapper.columns[key]
        column_type = column.type
        python_type = column_type.python_type
        return python_type(value)
