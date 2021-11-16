from collections import namedtuple
from datetime import datetime
from io import StringIO
from math import exp
from click.testing import CliRunner
import pytest
import requests
from tests.test_classes import (
    BAD_DATE,
    GOOD_DATE,
    MockResponseCIFailing, 
    MockResponseCIPassing, 
    MockResponseWellUsed,
    MockResponseCommitsYes,
    MockResponseCommitsNo,
    MockResponseReleasesYes,
    MockResponseReleasesNo,
    MockResponseCISetUpYes,
    MockResponseCISetUpNo,
    MockResponseBugsYes,
    MockResponseBugsNo,
    MockResponseProductionReadyYes,
    MockResponseProductionReadyNoAlpha,
    MockResponseProductionReadyNoBeta,
    MockResponseProductionReadyNoOther,

)
from the_well_maintained_test.cli import cli
from the_well_maintained_test.utils import (
    yes_no, 
    change_log_check, 
    bug_responding, 
    ci_setup, 
    ci_passing, 
    well_used,
    commit_in_last_year,
    release_in_last_year,
    production_ready_check
)


def test_version():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert result.output.startswith("cli, version ")



@pytest.mark.parametrize(
    "test_input,expected", 
    [
        ["y\n", "[bold green]\tYes[bold]"], 
        ["n\n", "[bold red]\tNo[bold]"]
    ]
)
def test_yes_no(monkeypatch, test_input, expected):
    """
        2. Is there sufficient documentation?
        5. Are there sufficient tests?
        6. Are the tests running with the latest Language version?
        7. Are the tests running with the latest Integration version?
    """
    number_inputs = StringIO(test_input)
    monkeypatch.setattr('sys.stdin', number_inputs)
    assert yes_no('test') == expected


@pytest.mark.parametrize(
    "test_input,expected", 
    [
        [[200, 200], "[bold green]\tYes[bold]"], 
        [[404, 200], "[bold green]\tYes[bold]"], 
        [[200, 404], "[bold green]\tYes[bold]"], 
        [[404, 404], "[bold red]\tNo[bold]"]
    ]
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


def test_bug_response_yes():
    """
        4. Is someone responding to bug reports?
    """
    url = 'https://api.github.com/repos/simonw/db-to-sqlite/issues'
    auth=()
    BugComments = namedtuple('BugComments', ['text', 'create_date', 'bug_id'])
    today = datetime.now()
    bug_turn_around_time_reply_days = (today - datetime(2019, 7, 10)).days
    bug_comment_list = [BugComments('Text', '', 37)]

    days_since_last_bug_comment = (today - datetime(2021, 11, 6)).days
    expected = bug_responding(url, auth)
    message1 = f"The maintainer took {bug_turn_around_time_reply_days} days to respond to the bug report {bug_comment_list[0].bug_id}"
    message2 = f"It has been {days_since_last_bug_comment} days since a comment was made on the bug."
    actual = f"""[bold red]\t{message1}\n\t{message2}[bold]"""
    assert expected == actual



def test_bug_response_no(monkeypatch):
    """
        4. Is someone responding to bug reports?
    """
    auth=()
    def mock_get(*args, **kwargs):
            return MockResponseBugsNo()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)    
    url = 'https://fakeurl'
    actual = bug_responding(url, auth)
    expected = "\t[bold green]There have been no bugs reported that are still open.[bold]"
    assert actual == expected



def test_ci_setup_yes(monkeypatch):
    """
        8. Is there a Continuous Integration (CI) configuration?
    """
    auth=()
    def mock_get(*args, **kwargs):
            return MockResponseCISetUpYes()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)    
    url = 'https://fakeurl'
    actual = ci_setup(url, auth)
    expected = "[bold green]\tThere are 1 workflows[bold]\n[bold blue]\t - Test\n[bold]"
    assert actual == expected


def test_ci_setup_no(monkeypatch):
    """
        8. Is there a Continuous Integration (CI) configuration?
    """
    auth=()
    def mock_get(*args, **kwargs):
            return MockResponseCISetUpNo()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)    
    url = 'https://fakeurl'
    actual = ci_setup(url, auth)
    expected = "[bold red]There is no CI set up![bold]"
    assert actual == expected


def test_ci_passing_yes(monkeypatch):
    """
        9. Is the CI passing?
    """
    auth=()
    def mock_get(*args, **kwargs):
            return MockResponseCIPassing()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)    
    url = 'https://fakeurl'
    actual = ci_passing(url, auth)
    expected = "\t[green]Yes"
    assert actual == expected


def test_ci_passing_no(monkeypatch):
    """
        9. Is the CI passing?
    """
    auth=()
    def mock_get(*args, **kwargs):
            return MockResponseCIFailing()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)    
    url = 'https://fakeurl'
    actual = ci_passing(url, auth)
    expected = "\t[red]No"
    assert actual == expected


def test_well_used(monkeypatch):
    """
        10. Does it seem relatively well used?
    """
    auth=()
    def mock_get(*args, **kwargs):
            return MockResponseWellUsed()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)    
    url = 'https://fakeurl'
    actual = well_used(url, auth)
    message = "\tThe project has the following statistics:\n"
    message += f"\t- Watchers: 5\n"
    message += f"\t- Forks: 6\n"
    message += f"\t- Open Issues: 6\n"
    message += f"\t- Subscribers: 10"

    expected = message
    assert actual == expected


def test_commit_in_last_year_yes(monkeypatch):
    """
        11. Has there been a commit in the last year?
    """
    auth=()
    def mock_get(*args, **kwargs):
            return MockResponseCommitsYes()

    today = datetime.now()
    test_date = datetime.strptime(GOOD_DATE, '%Y-%m-%dT%H:%M:%SZ')
    days = (today-test_date).days


    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)    
    url = 'https://fakeurl'
    actual = commit_in_last_year(url, auth)
    expected = f"\t[green]Yes. The last commit was on {datetime.strftime(test_date, '%m-%d-%Y')} which was {days} days ago"
    assert actual == expected


def test_commit_in_last_year_no(monkeypatch):
    """
        11. Has there been a commit in the last year?
    """
    auth=()
    def mock_get(*args, **kwargs):
            return MockResponseCommitsNo()

    today = datetime.now()
    test_date = datetime.strptime(BAD_DATE, '%Y-%m-%dT%H:%M:%SZ')
    days = (today-test_date).days


    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)    
    url = 'https://fakeurl'
    actual = commit_in_last_year(url, auth)
    expected = f"\t[red]No. The last commit was {days} days ago"
    assert actual == expected


def test_release_in_last_year_yes(monkeypatch):
    """
        12. Has there been a release in the last year?
    """
    auth=()
    def mock_get(*args, **kwargs):
            return MockResponseReleasesYes()

    today = datetime.now()
    test_date = datetime.strptime(GOOD_DATE, '%Y-%m-%dT%H:%M:%SZ')
    
    days = (today-test_date).days

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)    
    url = 'https://fakeurl'
    actual = release_in_last_year(url, auth)
    expected = f"\t[green]Yes. The last commit was on {datetime.strftime(test_date, '%m-%d-%Y')} which was {days} days ago"
    assert actual == expected


def test_release_in_last_year_no(monkeypatch):
    """
        12. Has there been a release in the last year?
    """
    auth=()
    def mock_get(*args, **kwargs):
            return MockResponseReleasesNo()

    today = datetime.now()
    test_date = datetime.strptime(BAD_DATE, '%Y-%m-%dT%H:%M:%SZ')
    days = (today-test_date).days

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)    
    url = 'https://fakeurl'
    actual = release_in_last_year(url, auth)
    expected = f"\t[red]No. The last commit was {days} days ago"
    assert actual == expected


def test_production_ready_check_yes(monkeypatch):
    """
        1. Is it described as 'production ready'?
    """
    auth=()
    def mock_get(*args, **kwargs):
            return MockResponseProductionReadyYes()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)    
    url = 'https://fakeurl'
    actual = production_ready_check(url, auth)
    expected = f"[bold green]\tYes. The version is 1.0[bold]"
    assert actual == expected


def test_production_ready_check_no_alpha(monkeypatch):
    """
        1. Is it described as 'production ready'?
    """
    auth=()
    def mock_get(*args, **kwargs):
            return MockResponseProductionReadyNoAlpha()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)    
    url = 'https://fakeurl'
    actual = production_ready_check(url, auth)
    expected = f"[bold red]\tNo. The version is 1.0a which indicates an alpha version[bold]"
    assert actual == expected


def test_production_ready_check_no_beta(monkeypatch):
    """
        1. Is it described as 'production ready'?
    """
    auth=()
    def mock_get(*args, **kwargs):
            return MockResponseProductionReadyNoBeta()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)    
    url = 'https://fakeurl'
    actual = production_ready_check(url, auth)
    expected = f"[bold red]\tNo. The version is 1.0b which indicates a beta version[bold]"
    assert actual == expected


def test_production_ready_check_no_other(monkeypatch):
    """
        1. Is it described as 'production ready'?
    """
    auth=()
    def mock_get(*args, **kwargs):
            return MockResponseProductionReadyNoOther()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)    
    url = 'https://fakeurl'
    actual = production_ready_check(url, auth)
    expected = f"[bold red]\tNo.[bold]" 
    assert actual == expected
