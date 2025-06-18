@default:
    just --list

# run tests via pytest, creates coverage report, and then opens it up
test:
    uv run coverage run -m pytest
    uv run coverage html
    open htmlcov/index.html

# runs the pre-commit check command
check: lint mypy
    pre-commit run --all-files

# run ruff linting and formatting
lint:
    uv run ruff check --fix
    uv run ruff format

# opens the coverage index
coverage:
    open htmlcov/index.html

# prunes remote branches from github
prune:
    git remote prune origin

# removes all but main and dev local branch
gitclean:
    git branch | grep -v "main" | grep -v "dev"| xargs git branch -D


# run mypy on the files
mypy:
    uv run mypy pelican/plugins/pelican_to_sqlite/*.py --no-strict-optional


# generates the README.md file --help section
cog:
    cog -r README.md


# generates the README.md file --help section
docs:
    cog -r README.md
    cp README.md docs/index.md

# pulls from branch
sync branch:
    git switch {{branch}}
    git pull origin {{branch}}

pre-commit:
    pre-commit run --all-files
