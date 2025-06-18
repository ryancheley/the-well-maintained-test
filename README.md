# the-well-maintained-test

[![PyPI](https://img.shields.io/pypi/v/the-well-maintained-test.svg)](https://pypi.org/project/the-well-maintained-test/)
[![Changelog](https://img.shields.io/github/v/release/ryancheley/the-well-maintained-test?include_prereleases&label=changelog)](https://github.com/ryancheley/the-well-maintained-test/releases)
[![Tests](https://github.com/ryancheley/the-well-maintained-test/workflows/Test/badge.svg)](https://github.com/ryancheley/the-well-maintained-test/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/ryancheley/the-well-maintained-test/blob/master/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/ryancheley/the-well-maintained-test/main.svg)](https://results.pre-commit.ci/latest/github/ryancheley/the-well-maintained-test/main)



Programatically tries to answer the 12 questions from Adam Johnson's [blog post](https://adamj.eu/tech/2021/11/04/the-well-maintained-test/)

## Installation

### uv (recommended)

The preferred method of installation for this tool is [uv](https://docs.astral.sh/uv/).

    uv tool install the-well-maintained-test

### pipx

Alternatively, you can use [pipx](https://pypa.github.io/pipx/).

    pipx install the-well-maintained-test

### virtual environment

This tool can be installed in a virtual environment using pip:

Create your virtual environment

    python3 -m venv venv
    source venv/bin/activate

Install with pip

    python -m pip install the-well-maintained-test

## Authentication
The GitHub API will rate limit anonymous calls. You can authenticate yourself with a personal token (documentation on how to generate is [here](https://github.com/settings/tokens))

Run this command and paste in your new token:

    the-well-maintained-test auth

This will create a file called auth.json in your current directory containing the required value. To save the file at a different path or filename, use the `--auth=myauth.json` option.

## the-well-maintained-test --help

<!-- [[[cog
import cog
from the_well_maintained_test import cli
from click.testing import CliRunner
runner = CliRunner()
result = runner.invoke(cli.cli, ["--help"])
help = result.output.replace("Usage: cli", "Usage: the-well-maintained-test")
cog.out(
    "```\n{}\n```".format(help)
)
]]] -->
```
Usage: the-well-maintained-test [OPTIONS] COMMAND [ARGS]...

  Programatically tries to answer the 12 questions from Adam Johnson's blog post
  https://adamj.eu/tech/2021/11/04/the-well-maintained-test/

  package is a package on pypi you'd like to check:

      the-well-maintained-test package the-well-maintained-test

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  auth          Generates a json file with your GitHub Personal Token so...
  check         Check your GitHub API Usage Stats
  package       Name of a package on PyPi you'd like to check
  questions     List of questions tested
  requirements  Loop over a requirements.txt file

```
<!-- [[[end]]] -->

## Development

To contribute to this tool, first checkout the code. This project uses [uv](https://docs.astral.sh/uv/) for modern Python dependency management.

### Using uv (recommended)

    cd the-well-maintained-test
    uv sync --extra test

This will create a virtual environment and install all dependencies including test dependencies.

To run the tests:

    uv run pytest

### Alternative: Traditional setup

If you prefer not to use uv, you can still use traditional tools:

    cd the-well-maintained-test
    python3 -m venv venv
    source venv/bin/activate
    pip install -e '.[test]'

To run the tests:

    just test

### Development commands

With uv:

    # Run the CLI tool
    uv run the-well-maintained-test --help

    # Run tests
    uv run pytest

    # Run mypy
    uv run mypy src/the_well_maintained_test/*.py --no-strict-optional

    # Install development dependencies
    uv sync --extra dev

The commands below use the command runner [just](https://github.com/casey/just). If you would rather not use `just` the raw commands are also listed above.

To run `mypy` command you'll need to run

    mypy --install-types

Then, to run mypy:

    just mypy

OR the raw command is

    mypy src/the_well_maintained_test/*.py --no-strict-optional

You can also do a pre-commit check on the files by running

    just check

OR the raw commands are

    pre-commit run --all-files
    mypy src/the_well_maintained_test/*.py --no-strict-optional

This will run several pre-commit hooks, but before that it will run `mypy`
