from os import system
from pathlib import Path
from urllib.parse import urlparse

import click
import pkg_resources
import requests
import toml
from rich.padding import Padding

from the_well_maintained_test.helpers import (
    _get_package_github_url,
    _get_requirements_txt_file,
)

from . import utils
from .console import console
from .headers import headers
from .styles import (
    answer_link_style,
    answer_padding_style,
    answer_style,
    question_style,
    special_answer_padding_style,
    warning_style,
)
from .utils import (
    bug_responding,
    change_log_check,
    check_tests,
    ci_passing,
    ci_setup,
    commit_in_last_year,
    documentation_exists,
    framework_check,
    get_github_api_rate_limits,
    get_vulnerabilities,
    language_check,
    production_ready_check,
    release_in_last_year,
    save_auth,
    well_used,
)


@click.group()
@click.version_option()
def cli():  # pragma: no cover
    """
    Programatically tries to answer the 12 questions from Adam Johnson's
    blog post https://adamj.eu/tech/2021/11/04/the-well-maintained-test/

    package is a package on pypi you'd like to check:

        the-well-maintained-test package the-well-maintained-test

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
    """Generates a json file with your GitHub Personal Token so that you can have up to
    50,000 API calls instead of 60 for anonymous callers

        Args:\n
            auth (str): the name of the file you want to write to for your Personal Token. The default is auth.json
    """
    save_auth(auth)


@cli.command()
@click.option(
    "-n",
    "--name",
    type=click.STRING,
    help="Pass the name of the package to check",
)
@click.option(
    "-q",
    "--question",
    type=click.Choice(["all", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]),
    default="all",
    help="List of questions that are tested",
)
def questions(name: str, question: str) -> None:  # pragma: no cover
    "List of questions tested"
    with open(Path(pkg_resources.resource_filename(__name__, str(Path("data").joinpath("questions.toml"))))) as file:
        questions = toml.load(file)

    "List of URLs to use"
    with open(Path(pkg_resources.resource_filename(__name__, str(Path("data").joinpath("urls.toml"))))) as file:
        urls = toml.load(file)

    if question != "all":
        question_url = questions.get("question").get(question).get("question_url")
        console.print(questions.get("question").get(question).get("question_text"), style=question_style)
        console.print(
            Padding(questions.get("question").get(question).get("question_description"), answer_padding_style, style=answer_style)
        )
        question_link_verbiage = f'See {questions.get("question").get(question).get("question_link")} for the original source.'
        console.print(question_link_verbiage, style=answer_link_style)
        if name:
            question_function = (
                f"[bold green]function_name[/bold green]: {questions.get('question').get(question).get('question_function')}"
            )
            console.print(Padding(question_function, answer_padding_style, style=question_style + " italic"))
            url = urls.get("url").get(question_url).replace("{name}", name)
            github_url = _get_package_github_url(name)[1]
            parse_object = urlparse(github_url)
            author = parse_object.path.split("/")[-2]
            if "{author}" in url:
                url = url.replace("{author}", author)
            if "{default_branch}" in url:
                api_url = f"https://api.github.com/repos/{author}/{name}"
                default_branch = requests.get(api_url).json().get("default_branch")
                url = url.replace("{default_branch}", default_branch)

            if questions.get("question").get(question).get("headers_needed") == "N":
                console.print(getattr(utils, questions.get("question").get(question).get("question_function"))(url))
            else:
                console.print(getattr(utils, questions.get("question").get(question).get("question_function"))(url, headers))

    else:
        for _, v in questions.get("question").items():
            console.print(v.get("question_text"), style=question_style)


@cli.command()
@click.option(
    "-r",
    "--requirements-file",
    type=click.Path(exists=True),
    help="List of questions that are tested",
)
@click.option(
    "-o",
    "--output",
    type=click.Choice(["html", "txt"]),
    help="Show progress on test check",
)
def requirements(requirements_file, output):  # pragma: no cover
    "Loop over a requirements.txt file"
    packages = _get_requirements_txt_file(requirements_file)
    for package in packages:
        console.rule(f"[bold blue] {package[0]}")
        cmd = f"the-well-maintained-test package '{package[0]}'"
        system(cmd)
        if output == "html":
            console.save_html(
                f"output_{package[0].lower()}.html",
            )

        if output == "txt":
            console.save_text(f"output_{package[0].lower()}.txt")


@cli.command()
@click.option(
    "-r",
    "--resource",
    type=click.Choice(["code_scanning_upload", "core", "graphql", "integration_manifest", "search"]),
    default="core",
    show_default=True,
    help="Show progress on test check",
)
def check(resource: str):  # pragma: no cover
    """Check your GitHub API Usage Stats

    Args:\n
        resource (str): Which GitHub resource to check. See Options below.
    """

    message = get_github_api_rate_limits(headers, resource)
    console.print(Padding(message, answer_padding_style, style=answer_style))


@cli.command()
@click.argument("package", type=click.STRING, required=True)
@click.option(
    "-b",
    "--branch",
    type=click.STRING,
    help="The branch to check",
)
@click.option(
    "-p",
    "--progress",
    type=click.BOOL,
    default=True,
    help="Show or hide the progress on Test Checking Question",
)
@click.option(
    "-o",
    "--output",
    type=click.Choice(["html", "txt"]),
    help="Save the output as HTML or TXT",
)
def package(package: str, branch: str, progress: bool, output: str) -> None:  # pragma: no cover
    """Name of a package on PyPi you'd like to check

    Args:\n
        name (str): The name of the Package from PyPi
    """
    pypi_url = f"https://pypi.org/pypi/{package}/json"
    url = _get_package_github_url(package)[1]

    "url to a github repository you'd like to check"
    if url[-1] == "/":
        url = url.strip("/")

    with open(Path(pkg_resources.resource_filename(__name__, str(Path("data").joinpath("questions.toml"))))) as file:
        questions = toml.load(file)

    parse_object = urlparse(url)
    author = parse_object.path.split("/")[-2]
    package = parse_object.path.split("/")[-1]
    api_url = f"https://api.github.com/repos/{author}/{package}"
    if not branch:
        default_branch = requests.get(api_url).json().get("default_branch")
    else:
        default_branch = branch
    commits_url = f"https://api.github.com/repos/{author}/{package}/commits/{default_branch}"
    workflows_url = f"https://api.github.com/repos/{author}/{package}/actions/workflows"
    ci_status_url = f"https://api.github.com/repos/{author}/{package}/actions/runs"
    bugs_url = f"https://api.github.com/repos/{author}/{package}/issues?labels=bug"
    tree_url = f"https://api.github.com/repos/{author}/{package}/git/trees/{default_branch}?recursive=1"

    vulnerabilities = get_vulnerabilities(pypi_url)
    if vulnerabilities > 0:
        console.rule("[bold red]Vulnerabilities detected!!!")
        console.print(
            Padding(f"There are {vulnerabilities} vulnerabilities in this package", answer_padding_style, style=warning_style)
        )
        console.rule()

    console.print(questions.get("question").get("1").get("question_text"), style=question_style)
    console.print(Padding(production_ready_check(pypi_url), answer_padding_style, style=answer_style))

    console.print(questions.get("question").get("2").get("question_text"), style=question_style)
    console.print(Padding(documentation_exists(pypi_url), answer_padding_style, style=answer_style))

    console.print(questions.get("question").get("3").get("question_text"), style=question_style)
    console.print(Padding(change_log_check(pypi_url), answer_padding_style, style=answer_style))

    console.print(questions.get("question").get("4").get("question_text"), style=question_style)
    console.print(Padding(bug_responding(bugs_url, headers), answer_padding_style, style=answer_style))

    console.print(questions.get("question").get("5").get("question_text"), style=question_style)
    console.print(Padding(check_tests(tree_url, headers, progress), special_answer_padding_style, style=answer_style))

    console.print(questions.get("question").get("6").get("question_text"), style=question_style)
    console.print(Padding(language_check(pypi_url), answer_padding_style, style=answer_style))

    console.print(questions.get("question").get("7").get("question_text"), style=question_style)
    console.print(Padding(framework_check(pypi_url), answer_padding_style, style=answer_style))

    console.print(questions.get("question").get("8").get("question_text"), style=question_style)
    console.print(Padding(ci_setup(workflows_url, headers), answer_padding_style, style=answer_style))

    console.print(questions.get("question").get("9").get("question_text"), style=question_style)
    console.print(Padding(ci_passing(ci_status_url, headers), answer_padding_style, style=answer_style))

    console.print(questions.get("question").get("10").get("question_text"), style=question_style)
    console.print(Padding(well_used(api_url, headers), answer_padding_style, style=answer_style))

    console.print(questions.get("question").get("11").get("question_text"), style=question_style)
    console.print(Padding(commit_in_last_year(commits_url, headers), answer_padding_style, style=answer_style))

    console.print(questions.get("question").get("12").get("question_text"), style=question_style)
    console.print(Padding(release_in_last_year(pypi_url), answer_padding_style, style=answer_style))

    if output == "html":
        console.save_html("output.html")

    if output == "txt":
        console.save_text("output.txt")
