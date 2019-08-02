from contextlib import contextmanager
from functools import partial
from os.path import join
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from textwrap import dedent

from alembic import context
from alembic.config import Config
from alembic.script import ScriptDirectory
from microcosm.errors import LockedGraphError, NotBoundError


def make_alembic_config(temporary_dir, migrations_dir):
    """
    Alembic uses the `alembic.ini` file to configure where it looks for everything else.

    Not only is this file an unnecessary complication around a single-valued configuration,
    the single-value it chooses to use (the alembic configuration directory), hard-coding
    the decision that there will be such a directory makes Alembic setup overly verbose.

    Instead, generate a `Config` object with the values we care about.

    :returns: a usable instance of `Alembic.config.Config`

    """
    config = Config()
    config.set_main_option("temporary_dir", temporary_dir)
    config.set_main_option("migrations_dir", migrations_dir)
    return config


def make_script_directory(cls, config):
    """
    Alembic uses a "script directory"  to encapsulate its `env.py` file, its migrations
    directory, and its `script.py.mako` revision template.

    We'd rather not have such a directory at all as the default `env.py` rarely works
    without manipulation, migrations are better saved in a location within the source tree,
    and revision templates shouldn't vary between projects.

    Instead, generate a `ScriptDirectory` object, injecting values from the config.

    """
    temporary_dir = config.get_main_option("temporary_dir")
    migrations_dir = config.get_main_option("migrations_dir")

    return cls(
        dir=temporary_dir,
        version_locations=[migrations_dir],
    )


def get_alembic_environment_options(graph):
    try:
        return graph.config.alembic.environment_options
    except (AttributeError, LockedGraphError, NotBoundError):
        return dict()


def run_online_migration(self, Base, process_revision_directives):
    """
    Run an online migration using microcosm configuration.

    This function takes the place of the `env.py` file in the Alembic migration.

    """
    name = Base.resolve().__name__
    engine, Session = self.graph.sqlite(name)

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            # assumes that all models extend our base
            target_metadata=Base.metadata,

            # We use this to allow Alembic to automatically work around lack of
            # ALTER TABLE support in SQLite
            render_as_batch=True,

            process_revision_directives=process_revision_directives,

            **get_alembic_environment_options(self.graph),
        )

        with context.begin_transaction():
            context.run_migrations()


def make_script_py_mako(include_downgrade):
    """
    Generate the template for new migrations.

    This function takes the place of the `script.py.mako` file in the alembic directory.

    """
    template = dedent('''\
    """
    ${message}

    Revision ID: ${up_revision}
    Revises: ${down_revision | comma,n}
    Create Date: ${create_date}

    """
    from alembic import op
    import sqlalchemy as sa
    ${imports if imports else ""}

    # revision identifiers, used by Alembic.
    revision = ${repr(up_revision)}
    down_revision = ${repr(down_revision)}
    branch_labels = ${repr(branch_labels)}
    depends_on = ${repr(depends_on)}


    def upgrade():
        ${upgrades if upgrades else "pass"}
    ''')

    if include_downgrade:
        template += dedent('''\


        def downgrade():
            ${downgrades if downgrades else "pass"}
        ''')

    return template


@contextmanager
def patch_script_directory(graph, Base, include_downgrade=True, process_revision_directives=None):
    """
    Monkey patch the `ScriptDirectory` class, working around configuration assumptions.

    Changes include:
      - Using a generated, temporary directory (with a generated, temporary `script.py.mako`)
        instead of the assumed script directory.
      - Using our `make_script_directory` function instead of the default `ScriptDirectory.from_config`.
      - Using our `run_online_migration` function instead of the default `ScriptDirectory.run_env`.
      - Injecting the current object graph.
    """
    temporary_dir = mkdtemp()
    from_config_original = getattr(ScriptDirectory, "from_config")
    run_env_original = getattr(ScriptDirectory, "run_env")

    # use a temporary directory for the revision template
    with open(join(temporary_dir, "script.py.mako"), "w") as file_:
        file_.write(make_script_py_mako(include_downgrade))
        file_.flush()

    # monkey patch our script directory and migration logic
    setattr(ScriptDirectory, "from_config", classmethod(make_script_directory))
    setattr(
        ScriptDirectory,
        "run_env",
        partial(
            run_online_migration,
            ScriptDirectory,
            Base,
            process_revision_directives,
        ),
    )
    setattr(ScriptDirectory, "graph", graph)
    try:
        yield temporary_dir
    finally:
        # cleanup
        delattr(ScriptDirectory, "graph")
        setattr(ScriptDirectory, "run_env", run_env_original)
        setattr(ScriptDirectory, "from_config", from_config_original)
        rmtree(temporary_dir)


def get_migrations_dir(graph, name):
    """
    Resolve the migrations directory path.

    Either take the directory from a component of the object graph or by
    using the metaata's path resolution facilities.

    """
    try:
        migrations_base_dir = graph.sqlite_migrations_dir
    except (LockedGraphError, NotBoundError):
        migrations_base_dir = graph.metadata.get_path("sqlite-migrations")

    migrations_dir = Path(migrations_base_dir) / name

    if not migrations_dir.is_dir():
        raise Exception("Migrations dir must exist: {}".format(migrations_dir))
    return str(migrations_dir)
