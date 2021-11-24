import json
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


@click.command()
@click.version_option()
@click.argument("url")
def cli(url):  # pragma: no cover
    """
    Programatically tries to answer the 12 questions from \
        Adam Johnson's blog post https://adamj.eu/tech/2021/11/04/the-well-maintained-test/

    URL is a url to a github repository you'd like to check, for example:

        the-well-maintained-test 'https://github.com/ryancheley/the-well-maintained-test'

    """

    if url[-1] == "/":
        url = url.strip("/")

    parse_object = urlparse(url)
    author = parse_object.path.split("/")[-2]
    package = parse_object.path.split("/")[-1]
    api_url = f"https://api.github.com/repos/{author}/{package}"
    changelog_url = f"https://raw.githubusercontent.com/{author}/{package}/main/CHANGELOG.md"
    releases_url = f"https://www.github.com/{author}/{package}/releases"
    commits_url = f"https://api.github.com/repos/{author}/{package}/commits"
    workflows_url = f"https://api.github.com/repos/{author}/{package}/actions/workflows"
    ci_status_url = f"https://api.github.com/repos/{author}/{package}/actions/runs"
    bugs_url = f"https://api.github.com/repos/{author}/{package}/issues?labels=bug"
    changelog = requests.get(changelog_url, headers=headers)
    release = requests.get(releases_url, headers=headers)
    pypi_url = f"https://pypi.org/pypi/{package}/json"
    tree_url = f"https://api.github.com/repos/{author}/{package}/git/trees/main?recursive=1"

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
