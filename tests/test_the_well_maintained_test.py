from collections import namedtuple
from datetime import date, datetime
from io import StringIO

import pytest
import requests
from click.testing import CliRunner

from tests.test_classes import (
    BAD_DATE,
    GOOD_DATE,
    MockResponseBugsNo,
    MockResponseBugsYes,
    MockResponseCIFailing,
    MockResponseCIPassing,
    MockResponseCISetUpNo,
    MockResponseCISetUpYes,
    MockResponseCommentList,
    MockResponseCommitsNo,
    MockResponseCommitsYes,
    MockResponseDocumentationNo,
    MockResponseDocumentationYes,
    MockResponseFrameworkCheck,
    MockResponseLanguageCheck,
    MockResponseProductionReadyNo,
    MockResponseProductionReadyYes,
    MockResponseReleasesNo,
    MockResponseReleasesYes,
    MockResponseWellUsed,
)
from the_well_maintained_test.cli import cli
from the_well_maintained_test.utils import (
    _get_bug_comment_list,
    bug_responding,
    change_log_check,
    ci_passing,
    ci_setup,
    commit_in_last_year,
    documentation_exists,
    framework_check,
    language_check,
    production_ready_check,
    release_in_last_year,
    well_used,
    yes_no,
)


def test_version():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert result.output.startswith("cli, version ")


@pytest.mark.parametrize(
    "test_input,expected",
    [["y\n", "[bold green]\tYes[bold]"], ["n\n", "[bold red]\tNo[bold]"]],
)
def test_yes_no(monkeypatch, test_input, expected):
    """
    5. Are there sufficient tests?
    6. Are the tests running with the latest Language version?
    7. Are the tests running with the latest Integration version?
    """
    number_inputs = StringIO(test_input)
    monkeypatch.setattr("sys.stdin", number_inputs)
    assert yes_no("test") == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        [[200, 200], "[bold green]\tYes[bold]"],
        [[404, 200], "[bold green]\tYes[bold]"],
        [[200, 404], "[bold green]\tYes[bold]"],
        [[404, 404], "[bold red]\tNo[bold]"],
    ],
)
def test_changelog(test_input, expected):
    """
    3. Is there a changelog?
    """
    changelog = requests.models.Response()
    changelog.status_code = test_input[0]
    release = requests.models.Response()
    release.status_code = test_input[1]

    test = change_log_check(changelog=changelog, release=release)
    assert test == expected


def test_bug_response_yes(monkeypatch):
    """
    4. Is someone responding to bug reports?
    """

    def mock_get_bug_comment(url, auth):
        BugComments = namedtuple("BugComments", ["text", "create_date"])
        return [BugComments(text="Test", create_date=datetime.today())]

    def mock_get(*args, **kwargs):
        return MockResponseBugsYes()

    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl/17/timeline"

    auth = ()
    monkeypatch.setattr("the_well_maintained_test.utils._get_bug_comment_list", mock_get_bug_comment)

    today = date.today()

    bug_comment_list = _get_bug_comment_list(url, auth)

    bug_turn_around_time_reply_days = (today - bug_comment_list[0].create_date.date()).days

    days_since_last_bug_comment = 0
    expected = bug_responding(url, auth)
    message1 = f"The maintainer took {bug_turn_around_time_reply_days} days to respond to the bug report"
    message2 = f"It has been {days_since_last_bug_comment} days since a comment was made on the bug."
    actual = f"""[bold red]\t{message1}\n\t{message2}[bold]"""
    assert expected == actual


def test__get_bug_comment_list(monkeypatch):
    """A helper function to get the details of the comments for bugs

    Args:
        monkeypatch ([type]): [description]
    """
    BugComments = namedtuple("BugComments", ["text", "create_date"])
    auth = ()

    def mock_get(*args, **kwargs):
        return MockResponseCommentList()

    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl/17/timeline"
    actual = _get_bug_comment_list(url, auth)
    expected = [
        BugComments(
            text="This is the body.",
            create_date=datetime(2019, 7, 14, 0, 0, 0),
        )
    ]
    assert actual == expected


def test_bug_response_no(monkeypatch):
    """
    4. Is someone responding to bug reports?
    """
    auth = ()

    def mock_get(*args, **kwargs):
        return MockResponseBugsNo()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = bug_responding(url, auth)
    expected = "\t[bold green]There have been no bugs reported that are still open.[bold]"
    assert actual == expected


def test_ci_setup_yes(monkeypatch):
    """
    8. Is there a Continuous Integration (CI) configuration?
    """
    auth = ()

    def mock_get(*args, **kwargs):
        return MockResponseCISetUpYes()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = ci_setup(url, auth)
    expected = "[bold green]\tThere are 1 workflows[bold]\n[bold blue]\t - Test\n[bold]"
    assert actual == expected


def test_ci_setup_no(monkeypatch):
    """
    8. Is there a Continuous Integration (CI) configuration?
    """
    auth = ()

    def mock_get(*args, **kwargs):
        return MockResponseCISetUpNo()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = ci_setup(url, auth)
    expected = "[bold red]There is no CI set up![bold]"
    assert actual == expected


def test_ci_passing_yes(monkeypatch):
    """
    9. Is the CI passing?
    """
    auth = ()

    def mock_get(*args, **kwargs):
        return MockResponseCIPassing()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = ci_passing(url, auth)
    expected = "\t[green]Yes"
    assert actual == expected


def test_ci_passing_no(monkeypatch):
    """
    9. Is the CI passing?
    """
    auth = ()

    def mock_get(*args, **kwargs):
        return MockResponseCIFailing()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = ci_passing(url, auth)
    expected = "\t[red]No"
    assert actual == expected


def test_well_used(monkeypatch):
    """
    10. Does it seem relatively well used?
    """
    auth = ()

    def mock_get(*args, **kwargs):
        return MockResponseWellUsed()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = well_used(url, auth)
    message = "\tThe project has the following statistics:\n"
    message += "\t- Watchers: 5\n"
    message += "\t- Forks: 6\n"
    message += "\t- Open Issues: 6\n"
    message += "\t- Subscribers: 10"

    expected = message
    assert actual == expected


def test_commit_in_last_year_yes(monkeypatch):
    """
    11. Has there been a commit in the last year?
    """
    auth = ()

    def mock_get(*args, **kwargs):
        return MockResponseCommitsYes()

    today = datetime.now()
    test_date = datetime.strptime(GOOD_DATE, "%Y-%m-%dT%H:%M:%SZ")
    days = (today - test_date).days

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = commit_in_last_year(url, auth)
    expected = f"\t[green]Yes. The last commit was on {datetime.strftime(test_date, '%m-%d-%Y')} which was {days} days ago"
    assert actual == expected


def test_commit_in_last_year_no(monkeypatch):
    """
    11. Has there been a commit in the last year?
    """
    auth = ()

    def mock_get(*args, **kwargs):
        return MockResponseCommitsNo()

    today = datetime.now()
    test_date = datetime.strptime(BAD_DATE, "%Y-%m-%dT%H:%M:%SZ")
    days = (today - test_date).days

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = commit_in_last_year(url, auth)
    expected = f"\t[red]No. The last commit was {days} days ago"
    assert actual == expected


def test_release_in_last_year_yes(monkeypatch):
    """
    12. Has there been a release in the last year?
    """
    auth = ()

    def mock_get(*args, **kwargs):
        return MockResponseReleasesYes()

    today = datetime.now()
    test_date = datetime.strptime(GOOD_DATE, "%Y-%m-%dT%H:%M:%SZ")

    days = (today - test_date).days

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = release_in_last_year(url, auth)
    expected = f"\t[green]Yes. The last commit was on {datetime.strftime(test_date, '%m-%d-%Y')} which was {days} days ago"
    assert actual == expected


def test_release_in_last_year_no(monkeypatch):
    """
    12. Has there been a release in the last year?
    """
    auth = ()

    def mock_get(*args, **kwargs):
        return MockResponseReleasesNo()

    today = datetime.now()
    test_date = datetime.strptime(BAD_DATE, "%Y-%m-%dT%H:%M:%SZ")
    days = (today - test_date).days

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = release_in_last_year(url, auth)
    expected = f"\t[red]No. The last commit was {days} days ago"
    assert actual == expected


def test_production_ready_check_yes(monkeypatch):
    """
    1. Is it described as 'production ready'?
    """

    def mock_get(*args, **kwargs):
        return MockResponseProductionReadyYes()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = production_ready_check(url)
    expected = "\t[bold green]The project is set to Development Status[bold] [blue]Alpha"
    assert actual == expected


def test_production_ready_check_no(monkeypatch):
    """
    1. Is it described as 'production ready'?
    """

    def mock_get(*args, **kwargs):
        return MockResponseProductionReadyNo()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = production_ready_check(url)
    expected = "\t[bold red]\tThere is no Development Status for this package. It is currently at version 0.5[bold]"
    assert actual == expected


def test_document_exists_yes(monkeypatch):
    """
    2. Is there sufficient documentation?
    """

    def mock_get(*args, **kwargs):
        return MockResponseDocumentationYes()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = documentation_exists(url)
    expected = "\t[bold green]Documentation can be found at https://fakeurl/blob/main/README.md[bold]"
    assert actual == expected


def test_document_exists_no(monkeypatch):
    """
    2. Is there sufficient documentation?
    """

    def mock_get(*args, **kwargs):
        return MockResponseDocumentationNo()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = documentation_exists(url)
    expected = "\t[bold red]There is no documentation for this project[bold]"
    assert actual == expected


def test_language_check(monkeypatch):
    """
    6. Are the tests running with the latest Language version?
    """

    def mock_get(*args, **kwargs):
        return MockResponseLanguageCheck()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = language_check(url)
    expected = "\t[bold blue]The project supports the following programming languages[bold]\n\t\t- Python 3.6\n\t\t- Python 3.7\n"
    assert actual == expected


def test_framework_check_exists(monkeypatch):
    """
    7. Are the tests running with the latest Integration version?
    """

    def mock_get(*args, **kwargs):
        return MockResponseFrameworkCheck()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = framework_check(url)
    expected = "\t[bold blue]The project supports the following framework as it's latest[bold] Framework Django 3.2"
    assert actual == expected


def test_framework_check_does_not_exist(monkeypatch):
    """
    7. Are the tests running with the latest Integration version?
    """

    def mock_get(*args, **kwargs):
        return MockResponseLanguageCheck()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = framework_check(url)
    expected = "\t[bold blue]This project has no associated frameworks"
    assert actual == expected
