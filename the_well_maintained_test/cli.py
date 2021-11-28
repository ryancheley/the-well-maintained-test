import json
import pathlib
from urllib.parse import urlparse

import click
import requests
from rich.console import Console
from rich.padding import Padding
from rich.prompt import Prompt

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

console = Console()
question_style = "bold blue"
answer_style = "italic"
answer_padding_style = (1, 0, 1, 4)
special_answer_padding_style = (0, 0, 0, 4)

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
def auth(auth: str) -> None:  # pragma: no cover
    "Save authentication credentials to a JSON file"
    console.print("Create a GitHub personal user token and paste it here:")
    personal_token = Prompt.ask("Personal token")
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
@click.option(
    "-p",
    "--progress",
    type=click.BOOL,
    default=True,
    help="Show progress on test check",
)
def url(url: str, branch: str, progress: bool) -> None:  # pragma: no cover
    "url to a github repository you'd like to check"
    if url[-1] == "/":
        url = url.strip("/")

    with open("questions.json") as f:
        questions = json.load(f)

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
    commits_url = f"https://api.github.com/repos/{author}/{package}/commits/{default_branch}"
    workflows_url = f"https://api.github.com/repos/{author}/{package}/actions/workflows"
    ci_status_url = f"https://api.github.com/repos/{author}/{package}/actions/runs"
    bugs_url = f"https://api.github.com/repos/{author}/{package}/issues?labels=bug"
    changelog = requests.get(changelog_url, headers=headers)
    release = requests.get(releases_url, headers=headers)
    pypi_url = f"https://pypi.org/pypi/{package}/json"
    tree_url = f"https://api.github.com/repos/{author}/{package}/git/trees/{default_branch}?recursive=1"

    console.print(questions.get("1"), style=question_style)
    console.print(Padding(production_ready_check(pypi_url), answer_padding_style, style=answer_style))

    console.print(questions.get("2"), style=question_style)
    console.print(Padding(documentation_exists(pypi_url), answer_padding_style, style=answer_style))

    console.print(questions.get("3"), style=question_style)
    console.print(Padding(change_log_check(changelog, release), answer_padding_style, style=answer_style))

    console.print(questions.get("4"), style=question_style)
    console.print(Padding(bug_responding(bugs_url, headers), answer_padding_style, style=answer_style))

    console.print(questions.get("5"), style=question_style)
    console.print(Padding(check_tests(tree_url, headers, progress), special_answer_padding_style, style=answer_style))

    console.print(questions.get("6"), style=question_style)
    console.print(Padding(language_check(pypi_url), answer_padding_style, style=answer_style))

    console.print(questions.get("7"), style=question_style)
    console.print(Padding(framework_check(pypi_url), answer_padding_style, style=answer_style))

    console.print(questions.get("8"), style=question_style)
    console.print(Padding(ci_setup(workflows_url, headers), answer_padding_style, style=answer_style))

    console.print(questions.get("9"), style=question_style)
    console.print(Padding(ci_passing(ci_status_url, headers), answer_padding_style, style=answer_style))

    console.print(questions.get("10"), style=question_style)
    console.print(Padding(well_used(api_url, headers), answer_padding_style, style=answer_style))

    console.print(questions.get("11"), style=question_style)
    console.print(Padding(commit_in_last_year(commits_url, headers), answer_padding_style, style=answer_style))

    console.print(questions.get("12"), style=question_style)
    console.print(Padding(release_in_last_year(pypi_url), answer_padding_style, style=answer_style))


@cli.command()
@click.option(
    "-q",
    "--question",
    type=click.STRING,
    default="all",
    help="List of questions that are tested",
)
def questions(question: str) -> None:  # pragma: no cover
    "List of questions tested"
    with open("questions.json") as f:
        questions = json.load(f)

    if question != "all":
        console.print(questions.get(question), style=question_style)
    else:
        for _, v in questions.items():
            console.print(v, style=question_style)
