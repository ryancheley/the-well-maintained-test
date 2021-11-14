from datetime import datetime
import io
import sys
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
    release_in_last_year
)


def test_version():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert result.output.startswith("cli, version ")




def test_yes_no(monkeypatch):
    """
        1. Is it described as 'production ready'?
        2. Is there sufficient documentation?
        5. Are there sufficient tests?
        6. Are the tests running with the latest Language version?
        7. Are the tests running with the latest Integration version?
    """
    pass


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


def test_bug_response_yes(monkeypatch):
    """
        4. Is someone responding to bug reports?
    """
    auth=()
    def mock_get(*args, **kwargs):
            return MockResponseBugsYes()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)    
    url = 'https://fakeurl'
    actual = bug_responding(url, auth)
    expected = "\t[green]Yes"
    assert actual == expected



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


