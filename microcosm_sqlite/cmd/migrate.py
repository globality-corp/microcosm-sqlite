"""
Alembic CLI with simplified configuration.

Alembic is a terrific tool that makes some unfortunate choices about configuration,
expecting a verbose directory structure with several layers of configuration.

This module monkey patches Alembic's CLI tool to work better within a microcosm.

To use this entry enty point instead of the Alembic CLI:

 0. Don't use `alembic init`

 1. Define a `Base` like

        Base = DataSet.create("foo")

 2. Add a `sqlite-migrations/foo` directory within your source tree.

    This directory does not need to be an importable Python module, but it should
    be included as part of your distribution so that migrations ship with the service.

 3. Initialize your object graph (including your models):

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

 4. Write an entry point that invokes the `main` function with the object graph:

        main(graph, Base)

"""
from sys import argv

from alembic.config import CommandLine

from microcosm_sqlite.alembic import (
    get_migrations_dir,
    make_alembic_config,
    patch_script_directory,
)


def main(graph, Base, include_downgrade=True, *args):
    """
    Entry point for invoking Alembic's `CommandLine`.

    Alembic's CLI defines its own argument parsing and command invocation; we want
    to use these directly but define configuration our own way. This function takes
    the behavior of `CommandLine.main()` and reinterprets it with our patching.

    :param graph: an initialized object graph
    :param migration_dir: the path to the migrations directory

    """
    name = Base.resolve().__name__
    migrations_dir = get_migrations_dir(graph, name)

    cli = CommandLine()
    options = cli.parser.parse_args(args if args else argv[1:])
    if not hasattr(options, "cmd"):
        cli.parser.error("too few arguments")
    if options.cmd[0].__name__ == "init":
        cli.parser.error("Alembic 'init' command should not be used in the microcosm!")

    with patch_script_directory(
        graph=graph,
        Base=Base,
        include_downgrade=include_downgrade,
    ) as temporary_dir:
        config = make_alembic_config(temporary_dir, migrations_dir)
        cli.run_cmd(config, options)
