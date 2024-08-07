#!/usr/bin/env python
from setuptools import find_packages, setup


project = "microcosm-sqlite"
version = "2.0.0"

setup(
    name=project,
    version=version,
    description="Opinionated persistence with SQLite",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp/microcosm-sqlite",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.11",
    keywords="microcosm",
    install_requires=[
        "SQLAlchemy-Utils>=0.33.3",
        "SQLAlchemy>=1.2.0",
        "alembic>=1.0.11",
        "microcosm>=4.0.0",
    ],
    extras_require={
        "test": [
            "coverage>=3.7.1",
            "PyHamcrest>=1.8.5",
            "pytest-cov>=5.0.0",
            "pytest>=6.2.5",
        ],
        "lint": [
            "flake8",
            "flake8-print",
            "flake8-isort",
        ],
        "typehinting": [
            "mypy",
            "types-setuptools",
        ],
    },
    setup_requires=[
    ],
    dependency_links=[
    ],
    entry_points={
        "microcosm.factories": [
            "sqlite = microcosm_sqlite.factories:SQLiteBindFactory",
            "sqlite_builder = microcosm_sqlite.builders:SQLiteBuilder",
            "sqlite_dumper = microcosm_sqlite.dumpers:SQLiteDumper",
        ],
    },
)
