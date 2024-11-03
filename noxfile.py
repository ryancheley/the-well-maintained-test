import nox

PYTHON_VERSIONS = [
    "3.8",
    "3.9",
    "3.10",
    "3.11",
    "3.12",
    "3.13",
]


@nox.session(python=PYTHON_VERSIONS)
def tests(session):
    # Install pytest and any other test dependencies
    session.install("pytest")
    session.install("pytest-cov")

    # Install the package itself
    session.install(".")

    # Run pytest with coverage reporting
    session.run("pytest", "--cov", "--cov-report=term-missing", *session.posargs)
