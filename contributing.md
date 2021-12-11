# Contributing

To contribute to this library, first checkout the code. Then create a new virtual environment:

    cd toggl-to-sqlite
    python -m venv venv
    source venv/bin/activate

Now install the dependencies and tests:

    pip install -e '.[test]'

## Running the tests

To run the tests:

    pytest

## Code style

This library uses

* [Black](https://github.com/psf/black) and [Flake8](https://github.com/PyCQA/flake8) for code formatting.
* [isort](https://github.com/PyCQA/isort) to sort packages

The correct version of these libraries will be installed by `pip install -e '.[test]'` - you can run `pre-commit run --all-files` in the root directory to apply those formatting rules.
