"""
Checks that no migration is necessary.

1. Initialize your object graph (including your models):

       from microcosm.api import create_object_graph

       graph = create_object_graph(
           name="example",
           loader=load_from_dict(
               sqlite=dict(
                   use_foreign_keys="False",
               )
           )
       )

   The migrations directory is loaded by default assuming that the `name` attribute
   is a module name (though this behavior can be customized; see `microcosm.metadata:Metadata`)
   or by wiring up a string as the "migrations_dir" component of the graph.

   Note that `use_foreign_keys` must be false in order for Alembic batch
   migrations to work correctly.

2. Write an entry point that invokes the `main` function with the object graph:

       main(graph, Base)

"""
import shutil
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from alembic.config import CommandLine

from microcosm_sqlite.alembic import (
    get_migrations_dir,
    make_alembic_config,
    patch_script_directory,
)


class StaleDBError(Exception):
    pass


@contextmanager
def make_tmp_migrations_dir(migrations_dir_str):
    migrations_dir = Path(migrations_dir_str)
    with TemporaryDirectory() as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        for path in migrations_dir.glob("*.py"):
            shutil.copy(str(path), str(tmp_dir / path.name))
        yield tmp_dir


def process_revision_directives(context, revision, directives):
    script = directives[0]

    if script.upgrade_ops.ops:
        raise StaleDBError(f"Unexpected upgrade_ops {repr(script.upgrade_ops.ops)}")

    if script.downgrade_ops.ops:
        raise StaleDBError(f"Unexpected downgrade_ops {repr(script.downgrade_ops.ops)}")


def main(graph, Base):
    """
    Entry point for invoking Alembic's `CommandLine`.

    Runs revision --autogenerate to make sure no migration is necessary.

    Alembic's CLI defines its own argument parsing and command invocation; we want
    to use these directly but define configuration our own way. This function takes
    the behavior of `CommandLine.main()` and reinterprets it with our patching.

    :param graph: an initialized object graph

    """
    name = Base.resolve().__name__
    migrations_dir = get_migrations_dir(graph, name)

    cli = CommandLine()
    args = [
        "revision",
        "--autogenerate",
        "-m",
        "'Should be empty.'",
    ]
    options = cli.parser.parse_args(args)

    with patch_script_directory(
        graph=graph,
        Base=Base,
        process_revision_directives=process_revision_directives,
    ) as tmp_script_dir:
        with make_tmp_migrations_dir(migrations_dir) as tmp_migrations_dir:
            config = make_alembic_config(tmp_script_dir, str(tmp_migrations_dir))
            cli.run_cmd(config, options)
