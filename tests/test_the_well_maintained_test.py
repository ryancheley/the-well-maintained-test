from collections import namedtuple
from datetime import date, datetime
from time import localtime, strftime

import pytest
import requests
from click.testing import CliRunner

from tests.test_classes import (
    BAD_DATE,
    BAD_DATE_Z,
    GOOD_DATE,
    GOOD_DATE_Z,
    MockGitHubFileCheckAPIWithOutTestFiles,
    MockGitHubFileCheckAPIWithTestFiles,
    MockResponseBugsNo,
    MockResponseBugsWithNoResponse,
    MockResponseBugsYes,
    MockResponseCIFailing,
    MockResponseCINoConclusion,
    MockResponseCIPassing,
    MockResponseCISetUpNo,
    MockResponseCISetUpYes,
    MockResponseCommentList,
    MockResponseCommitsNo,
    MockResponseCommitsYes,
    MockResponseContentBase64,
    MockResponseContentNotBase64,
    MockResponseDocumentationNo,
    MockResponseDocumentationYes,
    MockResponseFrameworkCheck,
    MockResponseGitHubRateLimit,
    MockResponseLanguageCheck,
    MockResponseProductionReadyNo,
    MockResponseProductionReadyYes,
    MockResponseProjectURLs,
    MockResponseReleasesNo,
    MockResponseReleasesYes,
    MockResponseTestFilesDoNotExist,
    MockResponseTestFilesExist,
    MockResponseTestFilesNoBlobs,
    MockResponseWellUsed,
    MockResponseWithoutVulnerabilities,
    MockResponseWithVulnerabilities,
)
from the_well_maintained_test.cli import cli
from the_well_maintained_test.helpers import (
    _check_verb_agreement,
    _get_requirements_txt_file,
)
from the_well_maintained_test.utils import (
    _get_bug_comment_list,
    _get_content,
    _get_release_date,
    _get_test_files,
    _test_method_count,
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
    well_used,
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
        [[200, 200], "[green]Yes"],
        [[404, 200], "[green]Yes"],
        [[200, 404], "[green]Yes"],
        [[404, 404], "[red]No"],
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
    headers = {}

    def mock_get_bug_comment(url, headers=headers):
        BugComments = namedtuple("BugComments", ["text", "create_date"])
        return [BugComments(text="Test", create_date=datetime.today())]

    def mock_get(*args, **kwargs):
        return MockResponseBugsYes()

    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl/17/timeline"

    headers = {}
    monkeypatch.setattr("the_well_maintained_test.utils._get_bug_comment_list", mock_get_bug_comment)

    today = date.today()

    bug_comment_list = _get_bug_comment_list(url, headers=headers)

    bug_turn_around_time_reply_days = (today - bug_comment_list[0].create_date.date()).days

    days_since_last_bug_comment = 0
    expected = bug_responding(url, headers=headers)
    message1 = f"The maintainer took {bug_turn_around_time_reply_days} days to respond to the bug report"
    message2 = f"It has been {days_since_last_bug_comment} days since a comment was made on the bug."
    actual = f"[green]{message1}\n{message2}"
    assert expected == actual


def test__get_bug_comment_list(monkeypatch):
    """A helper function to get the details of the comments for bugs

    Args:
        monkeypatch ([type]): [description]
    """
    BugComments = namedtuple("BugComments", ["text", "create_date"])
    headers = {}

    def mock_get(*args, **kwargs):
        return MockResponseCommentList()

    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl/17/timeline"
    actual = _get_bug_comment_list(url, headers=headers)
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
    headers = {}

    def mock_get(*args, **kwargs):
        return MockResponseBugsNo()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = bug_responding(url, headers=headers)
    expected = "[green]There have been no bugs reported that are still open."
    assert actual == expected


def test_bug_response_yes_no_response(monkeypatch):
    """
    4. Is someone responding to bug reports?
    """
    headers = {}

    def mock_get(*args, **kwargs):
        return MockResponseBugsWithNoResponse()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = bug_responding(url, headers=headers)
    expected = "[red]There is 1 bugs with no comments"
    assert actual == expected


def test_ci_setup_yes(monkeypatch):
    """
    8. Is there a Continuous Integration (CI) configuration?
    """
    headers = {}

    def mock_get(*args, **kwargs):
        return MockResponseCISetUpYes()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = ci_setup(url, headers=headers)
    expected = "[green]There is 1 workflows\n[green]- Test\n"
    assert actual == expected


def test_ci_setup_no(monkeypatch):
    """
    8. Is there a Continuous Integration (CI) configuration?
    """
    headers = {}

    def mock_get(*args, **kwargs):
        return MockResponseCISetUpNo()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = ci_setup(url, headers=headers)
    expected = "[red]There is no CI set up!"
    assert actual == expected


def test_ci_passing_yes(monkeypatch):
    """
    9. Is the CI passing?
    """
    headers = {}

    def mock_get(*args, **kwargs):
        return MockResponseCIPassing()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = ci_passing(url, headers=headers)
    expected = "[green]Yes"
    assert actual == expected


def test_ci_passing_no_conclusion(monkeypatch):
    """
    9. Is the CI passing?
    """
    headers = {}

    def mock_get(*args, **kwargs):
        return MockResponseCINoConclusion()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = ci_passing(url, headers=headers)
    expected = "[red]No"
    assert actual == expected


def test_ci_passing_no(monkeypatch):
    """
    9. Is the CI passing?
    """
    headers = {}

    def mock_get(*args, **kwargs):
        return MockResponseCIFailing()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = ci_passing(url, headers=headers)
    expected = "[red]No"
    assert actual == expected


def test_well_used(monkeypatch):
    """
    10. Does it seem relatively well used?
    """
    headers = {}

    def mock_get(*args, **kwargs):
        return MockResponseWellUsed()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = well_used(url, headers=headers)
    message = "The project has the following statistics:\n"
    message += "- Watchers: 5\n"
    message += "- Forks: 6\n"
    message += "- Open Issues: 6\n"
    message += "- Subscribers: 10"
    message = f"[green]{message}"

    expected = message
    assert actual == expected


def test_commit_in_last_year_yes(monkeypatch):
    """
    11. Has there been a commit in the last year?
    """
    headers = {}

    def mock_get(*args, **kwargs):
        return MockResponseCommitsYes()

    today = datetime.now()
    test_date = datetime.strptime(GOOD_DATE_Z, "%Y-%m-%dT%H:%M:%SZ")
    days = (today - test_date).days

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = commit_in_last_year(url, headers=headers)
    expected = f"[green]Yes. The last commit was on {datetime.strftime(test_date, '%m-%d-%Y')} which was {days} days ago"
    assert actual == expected


def test_commit_in_last_year_no(monkeypatch):
    """
    11. Has there been a commit in the last year?
    """
    headers = {}

    def mock_get(*args, **kwargs):
        return MockResponseCommitsNo()

    today = datetime.now()
    test_date = datetime.strptime(BAD_DATE_Z, "%Y-%m-%dT%H:%M:%SZ")
    days = (today - test_date).days

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = commit_in_last_year(url, headers=headers)
    expected = f"[red]No. The last commit was {days} days ago"
    assert actual == expected


def test_release_in_last_year_yes(monkeypatch):
    """
    12. Has there been a release in the last year?
    """

    def mock_get(*args, **kwargs):
        return MockResponseReleasesYes()

    today = datetime.now()
    test_date = datetime.strptime(GOOD_DATE, "%Y-%m-%dT%H:%M:%S")

    days = (today - test_date).days

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = release_in_last_year(url)
    expected = f"[green]Yes. The last release was on {datetime.strftime(test_date, '%m-%d-%Y')} which was {days} days ago"
    assert actual == expected


def test_release_in_last_year_no(monkeypatch):
    """
    12. Has there been a release in the last year?
    """

    def mock_get(*args, **kwargs):
        return MockResponseReleasesNo()

    today = datetime.now()
    test_date = datetime.strptime(BAD_DATE, "%Y-%m-%dT%H:%M:%S")
    days = (today - test_date).days

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = release_in_last_year(url)
    expected = f"[red]No. Version 1.1.1 was last released {days} days ago"
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
    expected = "[green]The project is set to Development Status [underline]Alpha"
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
    expected = "[red]There is no Development Status for this package. It is currently at version 0.5"
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
    expected = "[green]Documentation can be found at https://fakeurl/blob/main/README.md"
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
    expected = "[red]There is no documentation for this project"
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
    expected = "[green]The project supports the following programming languages\n- Python 3.6\n- Python 3.7\n"
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
    expected = "[green]The project supports the following framework as it's latest[bold] Framework Django 3.2"
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
    expected = "[green]This project has no associated frameworks"
    assert actual == expected


# TODO: Rewrite test
def test_check_tests_exist(monkeypatch):
    """
    5. Are there sufficient tests?
    """
    headers = {}

    def mock_get(*args, **kwargs):
        return MockGitHubFileCheckAPIWithTestFiles()

    def mock__get_content(url, headers):
        content = """
ZnJvbSBmdW5jdG9vbHMgaW1wb3J0IHBhcnRpYWwKZnJvbSBpbnNwZWN0IGlt
cG9ydCBQYXJhbWV0ZXIsIFNpZ25hdHVyZSwgc2lnbmF0dXJlCmZyb20gaW8g
aW1wb3J0IFN0cmluZ0lPCmZyb20gdW5pdHRlc3QgaW1wb3J0IG1vY2sKCmlt
cG9ydCBweXRlc3QKZnJvbSBkamFuZ28uY29yZS5tYW5hZ2VtZW50IGltcG9y
dCBCYXNlQ29tbWFuZCwgQ29tbWFuZEVycm9yLCBjYWxsX2NvbW1hbmQKZnJv
bSBkamFuZ28udGVzdCBpbXBvcnQgU2ltcGxlVGVzdENhc2UKZnJvbSByaWNo
LmNvbnNvbGUgaW1wb3J0IENvbnNvbGUKCmZyb20gZGphbmdvX3JpY2gubWFu
YWdlbWVudCBpbXBvcnQgUmljaENvbW1hbmQKZnJvbSB0ZXN0cy50ZXN0YXBw
Lm1hbmFnZW1lbnQuY29tbWFuZHMuZXhhbXBsZSBpbXBvcnQgQ29tbWFuZCBh
cyBFeGFtcGxlQ29tbWFuZAoKCmRlZiBzdHJpcF9hbm5vdGF0aW9ucyhvcmln
aW5hbDogU2lnbmF0dXJlKSAtPiBTaWduYXR1cmU6CiAgICByZXR1cm4gU2ln
bmF0dXJlKAogICAgICAgIHBhcmFtZXRlcnM9WwogICAgICAgICAgICBwYXJh
bS5yZXBsYWNlKGFubm90YXRpb249UGFyYW1ldGVyLmVtcHR5KQogICAgICAg
ICAgICBmb3IgcGFyYW0gaW4gb3JpZ2luYWwucGFyYW1ldGVycy52YWx1ZXMo
KQogICAgICAgIF0KICAgICkKCgpjbGFzcyBGYWtlVHR5U3RyaW5nSU8oU3Ry
aW5nSU8pOgogICAgZGVmIGlzYXR0eShzZWxmKSAtPiBib29sOgogICAgICAg
IHJldHVybiBUcnVlCgoKY2xhc3MgUmljaENvbW1hbmRUZXN0cyhTaW1wbGVU
ZXN0Q2FzZSk6CiAgICBkZWYgdGVzdF9pbml0X3NpZ25hdHVyZShzZWxmKToK
ICAgICAgICByY19zaWduYXR1cmUgPSBzdHJpcF9hbm5vdGF0aW9ucyhzaWdu
YXR1cmUoUmljaENvbW1hbmQuX19pbml0X18pKQoKICAgICAgICBhc3NlcnQg
cmNfc2lnbmF0dXJlID09IHNpZ25hdHVyZShCYXNlQ29tbWFuZC5fX2luaXRf
XykKCiAgICBkZWYgdGVzdF9leGVjdXRlX3NpZ25hdHVyZShzZWxmKToKICAg
ICAgICByY19zaWduYXR1cmUgPSBzdHJpcF9hbm5vdGF0aW9ucyhzaWduYXR1
cmUoUmljaENvbW1hbmQuZXhlY3V0ZSkpCgogICAgICAgIGFzc2VydCByY19z
aWduYXR1cmUgPT0gc2lnbmF0dXJlKEJhc2VDb21tYW5kLmV4ZWN1dGUpCgog
ICAgZGVmIHRlc3RfY29tYmluZWRfY29sb3JfZmxhZ3NfZXJyb3Ioc2VsZik6
CiAgICAgICAgd2l0aCBweXRlc3QucmFpc2VzKENvbW1hbmRFcnJvcikgYXMg
ZXhjaW5mbzoKICAgICAgICAgICAgY2FsbF9jb21tYW5kKCJleGFtcGxlIiwg
Ii0tbm8tY29sb3IiLCAiLS1mb3JjZS1jb2xvciIpCgogICAgICAgIGFzc2Vy
dCAoCiAgICAgICAgICAgIHN0cihleGNpbmZvLnZhbHVlKQogICAgICAgICAg
ICA9PSAiVGhlIC0tbm8tY29sb3IgYW5kIC0tZm9yY2UtY29sb3Igb3B0aW9u
cyBjYW4ndCBiZSB1c2VkIHRvZ2V0aGVyLiIKICAgICAgICApCgogICAgZGVm
IHRlc3Rfb3V0cHV0X25vbl90dHkoc2VsZik6CiAgICAgICAgc3Rkb3V0ID0g
U3RyaW5nSU8oKQoKICAgICAgICBjYWxsX2NvbW1hbmQoImV4YW1wbGUiLCBz
dGRvdXQ9c3Rkb3V0KQoKICAgICAgICBhc3NlcnQgc3Rkb3V0LmdldHZhbHVl
KCkgPT0gIkFsZXJ0IVxuIgoKICAgIGRlZiB0ZXN0X291dHB1dF90dHkoc2Vs
Zik6CiAgICAgICAgc3Rkb3V0ID0gRmFrZVR0eVN0cmluZ0lPKCkKCiAgICAg
ICAgY2FsbF9jb21tYW5kKCJleGFtcGxlIiwgc3Rkb3V0PXN0ZG91dCkKCiAg
ICAgICAgYXNzZXJ0IHN0ZG91dC5nZXR2YWx1ZSgpID09ICJceDFiWzE7MzFt
QWxlcnQhXHgxYlswbVxuIgoKICAgIGRlZiB0ZXN0X291dHB1dF90dHlfbm9f
Y29sb3Ioc2VsZik6CiAgICAgICAgc3Rkb3V0ID0gRmFrZVR0eVN0cmluZ0lP
KCkKCiAgICAgICAgY2FsbF9jb21tYW5kKCJleGFtcGxlIiwgIi0tbm8tY29s
b3IiLCBzdGRvdXQ9c3Rkb3V0KQoKICAgICAgICBhc3NlcnQgc3Rkb3V0Lmdl
dHZhbHVlKCkgPT0gIkFsZXJ0IVxuIgoKICAgIGRlZiB0ZXN0X291dHB1dF9m
b3JjZV9jb2xvcihzZWxmKToKICAgICAgICBzdGRvdXQgPSBTdHJpbmdJTygp
CgogICAgICAgIGNhbGxfY29tbWFuZCgiZXhhbXBsZSIsICItLWZvcmNlLWNv
bG9yIiwgc3Rkb3V0PXN0ZG91dCkKCiAgICAgICAgYXNzZXJ0IHN0ZG91dC5n
ZXR2YWx1ZSgpID09ICJceDFiWzE7MzFtQWxlcnQhXHgxYlswbVxuIgoKICAg
IGRlZiB0ZXN0X291dHB1dF9tYWtlX3JpY2hfY29uc29sZShzZWxmKToKICAg
ICAgICBzdGRvdXQgPSBGYWtlVHR5U3RyaW5nSU8oKQogICAgICAgIG1ha2Vf
Y29uc29sZSA9IHBhcnRpYWwoQ29uc29sZSwgbWFya3VwPUZhbHNlLCBoaWdo
bGlnaHQ9RmFsc2UpCiAgICAgICAgcGF0Y2hlciA9IG1vY2sucGF0Y2gub2Jq
ZWN0KEV4YW1wbGVDb21tYW5kLCAibWFrZV9yaWNoX2NvbnNvbGUiLCBtYWtl
X2NvbnNvbGUpCgogICAgICAgIHdpdGggcGF0Y2hlcjoKICAgICAgICAgICAg
Y2FsbF9jb21tYW5kKCJleGFtcGxlIiwgc3Rkb3V0PXN0ZG91dCkKCiAgICAg
ICAgYXNzZXJ0IHN0ZG91dC5nZXR2YWx1ZSgpID09ICJbYm9sZCByZWRdQWxl
cnQhWy9ib2xkIHJlZF1cbiIK
        """
        return content

    # # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setattr("the_well_maintained_test.utils._get_content", mock__get_content)
    url = "https://fakeurl"
    actual = check_tests(url, headers=headers, show_progress=True)
    expected = "[green]There are 8 tests in 1 files:\n- tests/admin_changelist/test_date_hierarchy.py\n"
    assert actual == expected


def test_check_tests_do_not_exist(monkeypatch):
    """
    5. Are there sufficient tests?
    """
    headers = {}

    def mock_get(*args, **kwargs):
        return MockGitHubFileCheckAPIWithOutTestFiles()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = check_tests(url, headers=headers, show_progress=True)
    expected = "[red]There are 0 tests!"
    assert actual == expected


def test__get_content_base64(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponseContentBase64()

    headers = {}
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = _get_content(url, headers)
    expected = "test"
    assert actual == expected


def test__get_content_not_base64(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponseContentNotBase64()

    headers = {}
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    with pytest.raises(TypeError):
        _get_content(url, headers)


def test__test_method_count():
    content = """
ZnJvbSBmdW5jdG9vbHMgaW1wb3J0IHBhcnRpYWwKZnJvbSBpbnNwZWN0IGlt
cG9ydCBQYXJhbWV0ZXIsIFNpZ25hdHVyZSwgc2lnbmF0dXJlCmZyb20gaW8g
aW1wb3J0IFN0cmluZ0lPCmZyb20gdW5pdHRlc3QgaW1wb3J0IG1vY2sKCmlt
cG9ydCBweXRlc3QKZnJvbSBkamFuZ28uY29yZS5tYW5hZ2VtZW50IGltcG9y
dCBCYXNlQ29tbWFuZCwgQ29tbWFuZEVycm9yLCBjYWxsX2NvbW1hbmQKZnJv
bSBkamFuZ28udGVzdCBpbXBvcnQgU2ltcGxlVGVzdENhc2UKZnJvbSByaWNo
LmNvbnNvbGUgaW1wb3J0IENvbnNvbGUKCmZyb20gZGphbmdvX3JpY2gubWFu
YWdlbWVudCBpbXBvcnQgUmljaENvbW1hbmQKZnJvbSB0ZXN0cy50ZXN0YXBw
Lm1hbmFnZW1lbnQuY29tbWFuZHMuZXhhbXBsZSBpbXBvcnQgQ29tbWFuZCBh
cyBFeGFtcGxlQ29tbWFuZAoKCmRlZiBzdHJpcF9hbm5vdGF0aW9ucyhvcmln
aW5hbDogU2lnbmF0dXJlKSAtPiBTaWduYXR1cmU6CiAgICByZXR1cm4gU2ln
bmF0dXJlKAogICAgICAgIHBhcmFtZXRlcnM9WwogICAgICAgICAgICBwYXJh
bS5yZXBsYWNlKGFubm90YXRpb249UGFyYW1ldGVyLmVtcHR5KQogICAgICAg
ICAgICBmb3IgcGFyYW0gaW4gb3JpZ2luYWwucGFyYW1ldGVycy52YWx1ZXMo
KQogICAgICAgIF0KICAgICkKCgpjbGFzcyBGYWtlVHR5U3RyaW5nSU8oU3Ry
aW5nSU8pOgogICAgZGVmIGlzYXR0eShzZWxmKSAtPiBib29sOgogICAgICAg
IHJldHVybiBUcnVlCgoKY2xhc3MgUmljaENvbW1hbmRUZXN0cyhTaW1wbGVU
ZXN0Q2FzZSk6CiAgICBkZWYgdGVzdF9pbml0X3NpZ25hdHVyZShzZWxmKToK
ICAgICAgICByY19zaWduYXR1cmUgPSBzdHJpcF9hbm5vdGF0aW9ucyhzaWdu
YXR1cmUoUmljaENvbW1hbmQuX19pbml0X18pKQoKICAgICAgICBhc3NlcnQg
cmNfc2lnbmF0dXJlID09IHNpZ25hdHVyZShCYXNlQ29tbWFuZC5fX2luaXRf
XykKCiAgICBkZWYgdGVzdF9leGVjdXRlX3NpZ25hdHVyZShzZWxmKToKICAg
ICAgICByY19zaWduYXR1cmUgPSBzdHJpcF9hbm5vdGF0aW9ucyhzaWduYXR1
cmUoUmljaENvbW1hbmQuZXhlY3V0ZSkpCgogICAgICAgIGFzc2VydCByY19z
aWduYXR1cmUgPT0gc2lnbmF0dXJlKEJhc2VDb21tYW5kLmV4ZWN1dGUpCgog
ICAgZGVmIHRlc3RfY29tYmluZWRfY29sb3JfZmxhZ3NfZXJyb3Ioc2VsZik6
CiAgICAgICAgd2l0aCBweXRlc3QucmFpc2VzKENvbW1hbmRFcnJvcikgYXMg
ZXhjaW5mbzoKICAgICAgICAgICAgY2FsbF9jb21tYW5kKCJleGFtcGxlIiwg
Ii0tbm8tY29sb3IiLCAiLS1mb3JjZS1jb2xvciIpCgogICAgICAgIGFzc2Vy
dCAoCiAgICAgICAgICAgIHN0cihleGNpbmZvLnZhbHVlKQogICAgICAgICAg
ICA9PSAiVGhlIC0tbm8tY29sb3IgYW5kIC0tZm9yY2UtY29sb3Igb3B0aW9u
cyBjYW4ndCBiZSB1c2VkIHRvZ2V0aGVyLiIKICAgICAgICApCgogICAgZGVm
IHRlc3Rfb3V0cHV0X25vbl90dHkoc2VsZik6CiAgICAgICAgc3Rkb3V0ID0g
U3RyaW5nSU8oKQoKICAgICAgICBjYWxsX2NvbW1hbmQoImV4YW1wbGUiLCBz
dGRvdXQ9c3Rkb3V0KQoKICAgICAgICBhc3NlcnQgc3Rkb3V0LmdldHZhbHVl
KCkgPT0gIkFsZXJ0IVxuIgoKICAgIGRlZiB0ZXN0X291dHB1dF90dHkoc2Vs
Zik6CiAgICAgICAgc3Rkb3V0ID0gRmFrZVR0eVN0cmluZ0lPKCkKCiAgICAg
ICAgY2FsbF9jb21tYW5kKCJleGFtcGxlIiwgc3Rkb3V0PXN0ZG91dCkKCiAg
ICAgICAgYXNzZXJ0IHN0ZG91dC5nZXR2YWx1ZSgpID09ICJceDFiWzE7MzFt
QWxlcnQhXHgxYlswbVxuIgoKICAgIGRlZiB0ZXN0X291dHB1dF90dHlfbm9f
Y29sb3Ioc2VsZik6CiAgICAgICAgc3Rkb3V0ID0gRmFrZVR0eVN0cmluZ0lP
KCkKCiAgICAgICAgY2FsbF9jb21tYW5kKCJleGFtcGxlIiwgIi0tbm8tY29s
b3IiLCBzdGRvdXQ9c3Rkb3V0KQoKICAgICAgICBhc3NlcnQgc3Rkb3V0Lmdl
dHZhbHVlKCkgPT0gIkFsZXJ0IVxuIgoKICAgIGRlZiB0ZXN0X291dHB1dF9m
b3JjZV9jb2xvcihzZWxmKToKICAgICAgICBzdGRvdXQgPSBTdHJpbmdJTygp
CgogICAgICAgIGNhbGxfY29tbWFuZCgiZXhhbXBsZSIsICItLWZvcmNlLWNv
bG9yIiwgc3Rkb3V0PXN0ZG91dCkKCiAgICAgICAgYXNzZXJ0IHN0ZG91dC5n
ZXR2YWx1ZSgpID09ICJceDFiWzE7MzFtQWxlcnQhXHgxYlswbVxuIgoKICAg
IGRlZiB0ZXN0X291dHB1dF9tYWtlX3JpY2hfY29uc29sZShzZWxmKToKICAg
ICAgICBzdGRvdXQgPSBGYWtlVHR5U3RyaW5nSU8oKQogICAgICAgIG1ha2Vf
Y29uc29sZSA9IHBhcnRpYWwoQ29uc29sZSwgbWFya3VwPUZhbHNlLCBoaWdo
bGlnaHQ9RmFsc2UpCiAgICAgICAgcGF0Y2hlciA9IG1vY2sucGF0Y2gub2Jq
ZWN0KEV4YW1wbGVDb21tYW5kLCAibWFrZV9yaWNoX2NvbnNvbGUiLCBtYWtl
X2NvbnNvbGUpCgogICAgICAgIHdpdGggcGF0Y2hlcjoKICAgICAgICAgICAg
Y2FsbF9jb21tYW5kKCJleGFtcGxlIiwgc3Rkb3V0PXN0ZG91dCkKCiAgICAg
ICAgYXNzZXJ0IHN0ZG91dC5nZXR2YWx1ZSgpID09ICJbYm9sZCByZWRdQWxl
cnQhWy9ib2xkIHJlZF1cbiIK
    """
    actual = _test_method_count(content)
    expected = 8
    assert actual == expected


def test__get_test_files_exist(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponseTestFilesExist()

    headers = {}
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = _get_test_files(url, headers)
    expected = [
        {
            "type": "blob",
            "path": "tests/test_management.py",
        },
        {
            "path": "friendship/tests/tests.py",
            "type": "blob",
        },
    ]
    assert actual == expected


def test__get_test_files_do_not_exist(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponseTestFilesDoNotExist()

    headers = {}
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = _get_test_files(url, headers)
    expected = []
    assert actual == expected


def test__get_test_files_no_blobs(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponseTestFilesNoBlobs()

    headers = {}
    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = _get_test_files(url, headers)
    expected = []
    assert actual == expected


def test__get_release_date():
    Release = namedtuple("Release", "version, upload_time")
    release = {
        "9.9.0": [
            {
                "upload_time": "2021-01-16T15:12:25",
            }
        ],
        "10.14.0": [
            {
                "upload_time": "2021-10-16T15:12:25",
            }
        ],
        "10.15.0a1": [
            {
                "upload_time": "2021-11-16T15:12:25",
            }
        ],
    }
    actual = _get_release_date(release)
    expected = [
        Release(version="10.14.0", upload_time="2021-10-16T15:12:25"),
        Release(version="9.9.0", upload_time="2021-01-16T15:12:25"),
    ]
    assert actual == expected


def test__get_release_date_missing():
    release = {
        "9.9.0": [],
    }
    actual = _get_release_date(release)
    expected = []
    assert actual == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        [0, "are"],
        [1, "is"],
        [2, "are"],
        [-1, "are"],
    ],
)
def test__check_verb_agreement(test_input, expected):
    assert _check_verb_agreement(test_input) == expected


def test__get_requirements_txt_file(tmpdir, monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponseProjectURLs()

    monkeypatch.setattr(requests, "get", mock_get)

    p = tmpdir.mkdir("sub").join("requirements.txt")
    p.write("Django==3.2.9")
    actual = _get_requirements_txt_file(p)
    expected = [
        ("Django", "https://github.com/django/django"),
    ]
    assert actual == expected


def test_get_github_api_rate_limits(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponseGitHubRateLimit()

    resource = "core"
    headers = {}

    monkeypatch.setattr(requests, "get", mock_get)
    reset_date = strftime("%Y-%m-%d %H:%M:%S", localtime(1372700873))
    actual = get_github_api_rate_limits(headers, resource)
    message = "You have used 1 out of 5000 calls.\n\n"
    message += "You have 4999 calls remaining.\n\n"
    message += f"Your limit will reset at {reset_date}."

    expected = message
    assert actual == expected


def test_get_vulnerabilities_yes(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponseWithVulnerabilities()

    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = get_vulnerabilities(url)
    expected = 3
    assert actual == expected


def test_get_vulnerabilities_no(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponseWithoutVulnerabilities()

    monkeypatch.setattr(requests, "get", mock_get)
    url = "https://fakeurl"
    actual = get_vulnerabilities(url)
    expected = 0
    assert actual == expected
