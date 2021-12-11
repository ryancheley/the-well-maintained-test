# the-well-maintained-test

[![PyPI](https://img.shields.io/pypi/v/the-well-maintained-test.svg)](https://pypi.org/project/the-well-maintained-test/)
[![Changelog](https://img.shields.io/github/v/release/ryancheley/the-well-maintained-test?include_prereleases&label=changelog)](https://github.com/ryancheley/the-well-maintained-test/releases)
[![Tests](https://github.com/ryancheley/the-well-maintained-test/workflows/Test/badge.svg)](https://github.com/ryancheley/the-well-maintained-test/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/ryancheley/the-well-maintained-test/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Imports: flake8](https://img.shields.io/badge/%20imports-flake8-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/flake8/)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/ryancheley/the-well-maintained-test/main.svg)](https://results.pre-commit.ci/latest/github/ryancheley/the-well-maintained-test/main)



Programatically tries to answer the 12 questions from Adam Johnson's [blog post](https://adamj.eu/tech/2021/11/04/the-well-maintained-test/)

## Installation

Install this tool using `pip`:

    $ pip install the-well-maintained-test


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

  URL is a url to a github repository you'd like to check, for example:

      the-well-maintained-test url 'https://github.com/ryancheley/the-well-
      maintained-test'

  Note: URL was deprecated and replaced with package starting in v0.9.0

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  auth          Generates a json file with your GitHub Personal Token so...
  check         Check your GitHub API Usage Stats
  package       Name of a package on PyPi you'd like to check
  questions     List of questions tested
  requirements  Loop over a requirements.txt file
  url           URL to a github repository you'd like to check.

```
<!-- [[[end]]] -->

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd the-well-maintained-test
    python -m venv venv
    source venv/bin/activate

Or if you are using `pipenv`:

    pipenv shell

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    just test

To run `mypy` command you'll need to run

    mypy --install-types

Then, to run mypy:

    just mypy

You can also do a pre-commit check on the files by running

    just check

This will run several pre-commit hooks, but before that it will run `mypy`
