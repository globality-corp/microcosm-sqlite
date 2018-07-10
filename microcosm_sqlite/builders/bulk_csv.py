from csv import DictReader

from microcosm_sqlite.builders.csv import CSVBuilder


class BulkCSVBuilder:
    def __init__(self, base_ctx_cls, graph):
        self.base_ctx_cls = base_ctx_cls
        self.graph = graph

    def build(self, model_fileobj):
        with self.base_ctx_cls.new_context(
            graph=self.graph,
            defer_foreign_keys=True,
        ) as context:
            for model, fileobj in model_fileobj:
                reader = DictReader(fileobj)
                builder = CSVBuilder(self.graph, model)

                for row in reader:
                    context.session.add(
                        builder.as_model(row),
                    )

            context.session.commit()
