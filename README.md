# the-well-maintained-test

[![PyPI](https://img.shields.io/pypi/v/the-well-maintained-test.svg)](https://pypi.org/project/the-well-maintained-test/)
[![Changelog](https://img.shields.io/github/v/release/ryancheley/the-well-maintained-test?include_prereleases&label=changelog)](https://github.com/ryancheley/the-well-maintained-test/releases)
[![Tests](https://github.com/ryancheley/the-well-maintained-test/workflows/Test/badge.svg)](https://github.com/ryancheley/the-well-maintained-test/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/ryancheley/the-well-maintained-test/blob/master/LICENSE)

Programatically tries to answer the 12 questions from Adam Johnson's blog post https://adamj.eu/tech/2021/11/04/the-well-maintained-test/

## Installation

Install this tool using `pip`:

    $ pip install the-well-maintained-test

## Usage

Usage instructions go here.

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

    pytest
