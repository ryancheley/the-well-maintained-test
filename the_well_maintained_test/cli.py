import json
import pathlib
from urllib.parse import urlparse

import click
import requests
from rich import print

from .utils import (
    bug_responding,
    change_log_check,
    check_tests,
    ci_passing,
    ci_setup,
    commit_in_last_year,
    documentation_exists,
    framework_check,
    language_check,
    production_ready_check,
    release_in_last_year,
    well_used,
)

try:  # pragma: no cover
    with open("auth.json") as f:
        data = json.load(f)
    headers = {
        "Authorization": f'token {data["github_personal_token"]}',
    }
except FileNotFoundError:  # pragma: no cover
    headers = {}


@click.group()
@click.version_option()
def cli():  # pragma: no cover
    """
    Programatically tries to answer the 12 questions from \
        Adam Johnson's blog post https://adamj.eu/tech/2021/11/04/the-well-maintained-test/
    URL is a url to a github repository you'd like to check, for example:
        the-well-maintained-test 'https://github.com/ryancheley/the-well-maintained-test'
    """
    pass


@cli.command()
@click.option(
    "-a",
    "--auth",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    default="auth.json",
    help="Path to save tokens to, defaults to auth.json",
)
def auth(auth):  # pragma: no cover
    "Save authentication credentials to a JSON file"
    click.echo("Create a GitHub personal user token and paste it here:")
    click.echo()
    personal_token = click.prompt("Personal token")
    if pathlib.Path(auth).exists():
        auth_data = json.load(open(auth))
    else:
        auth_data = {}
    auth_data["github_personal_token"] = personal_token
    open(auth, "w").write(json.dumps(auth_data, indent=4) + "\n")


@cli.command()
@click.argument(
    "url",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.option(
    "-b",
    "--branch",
    type=click.STRING,
    help="Branch to check",
)
def url(url, branch):  # pragma: no cover
    "url to a github repository you'd like to check"
    if url[-1] == "/":
        url = url.strip("/")

    parse_object = urlparse(url)
    author = parse_object.path.split("/")[-2]
    package = parse_object.path.split("/")[-1]
    api_url = f"https://api.github.com/repos/{author}/{package}"
    if not branch:
        default_branch = requests.get(api_url).json().get("default_branch")
    else:
        default_branch = branch
    changelog_url = f"https://raw.githubusercontent.com/{author}/{package}/{default_branch}/CHANGELOG.md"
    releases_url = f"https://www.github.com/{author}/{package}/releases"
    # TODO: addition of /{default_branch} below will break the methods and the tests.
    # Need to update as the return went from a [list] to a {dictionary}
    commits_url = f"https://api.github.com/repos/{author}/{package}/commits/{default_branch}"
    workflows_url = f"https://api.github.com/repos/{author}/{package}/actions/workflows"
    ci_status_url = f"https://api.github.com/repos/{author}/{package}/actions/runs"
    bugs_url = f"https://api.github.com/repos/{author}/{package}/issues?labels=bug"
    changelog = requests.get(changelog_url, headers=headers)
    release = requests.get(releases_url, headers=headers)
    pypi_url = f"https://pypi.org/pypi/{package}/json"
    tree_url = f"https://api.github.com/repos/{author}/{package}/git/trees/{default_branch}?recursive=1"

    print(production_ready_check(pypi_url))

    print(documentation_exists(pypi_url))

    print(change_log_check(changelog, release))

    print(bug_responding(bugs_url, headers))

    print(check_tests(tree_url, headers))

    print(language_check(pypi_url))

    print(framework_check(pypi_url))

    print(ci_setup(workflows_url, headers))

    print(ci_passing(ci_status_url, headers))

    print(well_used(api_url, headers))

    print(commit_in_last_year(commits_url, headers))

    print(release_in_last_year(pypi_url))


@cli.command()
@click.option(
    "-q",
    "--question",
    type=click.STRING,
    default="all",
    help="List of questions that are tested",
)
def questions(question):  # pragma: no cover
    "List of questions tested"
    questions = {
        "1": "1. Is it described as “production ready”?",
        "2": "2. Is there sufficient documentation?",
        "3": "3. Is there a changelog?",
        "4": "4. Is someone responding to bug reports?",
        "5": "5. Are there sufficient tests?",
        "6": "6. Are the tests running with the latest <Language> version?",
        "7": "7. Are the tests running with the latest <Integration> version?",
        "8": "8. Is there a Continuous Integration (CI) configuration?",
        "9": "9. Is the CI passing?",
        "10": "10. Does it seem relatively well used?",
        "11": "11. Has there been a commit in the last year?",
        "12": "12. Has there been a release in the last year?",
    }
    if question != "all":
        print(questions.get(question))
    else:
        for _, v in questions.items():
            print(v)
