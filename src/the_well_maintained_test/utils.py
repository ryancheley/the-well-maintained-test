import json
import re
from datetime import datetime
from gettext import ngettext
from operator import attrgetter
from pathlib import Path
from time import localtime, strftime

import requests
from rich.progress import Progress
from rich.prompt import Prompt

from the_well_maintained_test.console import console
from the_well_maintained_test.helpers import (
    _get_bug_comment_list,
    _get_content,
    _get_release_date,
    _get_test_files,
    _test_method_count,
)


def production_ready_check(pypi_api_url: str) -> str:
    response = requests.get(pypi_api_url).json()
    classifiers = response.get("info").get("classifiers")
    version = response.get("info").get("version")
    try:
        development_status = [s for s in classifiers if "Development Status" in s][0]
        development_status_start_point = re.search(r"Development Status :: [\d] \- ", development_status).span()[1]
        development_status_str_len = len(development_status)
        status = development_status[(development_status_start_point - development_status_str_len) :]
    except IndexError:
        development_status = []
    if development_status:
        message = f"[green]The project is set to Development Status [underline]{status}"
    else:
        message = f"[red]There is no Development Status for this package. It is currently at version {version}"
    return message


def documentation_exists(pypi_api_url: str) -> str:
    response = requests.get(pypi_api_url).json()
    docs = response.get("info").get("project_urls").get("Documentation")
    if docs:
        message = f"[green]Documentation can be found at {docs}"
    else:
        message = "[red]There is no documentation for this project"
    return message


def change_log_check(changelog_url: str) -> str:
    project_urls = requests.get(changelog_url).json().get("info").get("project_urls")
    change_log_types = ["Release notes", "Changelog"]
    if any(item in change_log_types for item in list(project_urls.keys())):
        return "[green]Yes"
    else:
        return "[red]No"


def bug_responding(bugs_url: str, headers: dict) -> str:
    """
    4. Is someone responding to bug reports?
    """

    r = requests.get(bugs_url, headers=headers).json()
    open_bug_count = len(r)
    bug_comment_list = []
    if open_bug_count == 0:
        message = "[green]There have been no bugs reported that are still open."
    else:
        for i in r:
            bug_create_date = datetime.strptime(i.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
            bug_comment_list = _get_bug_comment_list(i.get("timeline_url"), headers=headers)
        bug_comment_list = sorted(bug_comment_list, key=attrgetter("create_date"), reverse=True)
        if bug_comment_list:
            bug_turn_around_time_reply_days = (bug_comment_list[0].create_date - bug_create_date).days
            days_since_last_bug_comment = (datetime.utcnow() - bug_comment_list[0].create_date).days
            # TODO: add logic to better colorize the message
            message1 = f"The maintainer took {bug_turn_around_time_reply_days} "
            message1 += "days to respond to the bug report"
            message2 = f"It has been {days_since_last_bug_comment} days since a comment was made on the bug."
            message = f"[green]{message1}\n{message2}"
        else:
            verb = ngettext("is", "are", open_bug_count)
            message = f"[red]There {verb} {open_bug_count} bugs with no comments"
    return message


def check_tests(tree_url: str, headers: dict, show_progress: bool = True) -> str:
    """
    5. Are there sufficient tests?
    """
    test_list = _get_test_files(tree_url, headers=headers)
    total = len(test_list)
    test_files = 0
    test_functions = 0
    with Progress() as progress:
        test_file_reading_task = progress.add_task("[green]Processing...", total=total, visible=show_progress)
        for i in test_list:
            content = _get_content(i.get("url"), headers)
            test_count = _test_method_count(content)
            test_files += 1
            test_functions = test_functions + test_count
            progress.update(test_file_reading_task, advance=1)
        progress.remove_task(test_file_reading_task)
    if test_files == 0:
        message = "[red]There are 0 tests!"
    else:
        verb = ngettext("is", "are", test_functions)
        message = f"[green]There {verb} {test_functions} tests in {test_files} files:\n"
        for test in test_list:
            message += f"- {test.get('path')}\n"
    return message


def language_check(pypi_url: str) -> str:
    """
    6. Are the tests running with the latest Language version?
    """
    response = requests.get(pypi_url).json()
    classifiers = response.get("info").get("classifiers")
    languages = [s.replace("Programming Language :: Python :: ", "Python ") for s in classifiers if "Programming Language" in s]
    message = "[green]The project supports the following programming languages\n"
    for language in languages:
        message += f"- {language}\n"
    return message


# TODO: reqrite to list all frameworks as rich only shows IPython!
def framework_check(pypi_url: str) -> str:
    """
    7. Are the tests running with the latest Integration version?
    """
    response = requests.get(pypi_url).json()
    classifiers = response.get("info").get("classifiers")
    frameworks = [s.replace("Framework Django", "Framework").replace(" ::", "") for s in classifiers if "Framework" in s]
    if frameworks:
        framework = [s for s in classifiers if "Framework" in s][-1].replace(" :: ", " ")
        message = f"[green]The project supports the following framework as it's latest[bold] {framework}"
    else:
        message = "[green]This project has no associated frameworks"
    return message


def ci_setup(workflows_url: str, headers: dict) -> str:
    """
    8. Is there a Continuous Integration (CI) configuration?
    """
    r = requests.get(workflows_url, headers=headers).json()
    if r.get("total_count") > 0:
        workflow_count = r.get("total_count")
        verb = ngettext("is", "are", workflow_count)
        message = f"[green]There {verb} {workflow_count} workflows\n"
        for i in r.get("workflows"):
            message += f"[green]- {i.get('name')}\n"
        return message
    else:
        return "[red]There is no CI set up!"


def ci_passing(ci_status_url: str, headers: dict) -> str:
    """
    9. Is the CI passing?
    """
    r = requests.get(ci_status_url, headers=headers).json()
    conclusion = None
    try:
        conclusion = r.get("workflow_runs")[0].get("conclusion")
    except IndexError:
        pass
    if conclusion == "success":
        return "[green]Yes"
    else:
        return "[red]No"


def well_used(api_url: str, headers: dict) -> str:
    """
    10. Does it seem relatively well used?
    """
    r = requests.get(api_url, headers=headers).json()
    watchers = r.get("watchers")
    network_count = r.get("network_count")
    open_issues = r.get("open_issues")
    subscribers_count = r.get("subscribers_count")
    message = "The project has the following statistics:\n"
    message += f"- Watchers: {watchers}\n"
    message += f"- Forks: {network_count}\n"
    message += f"- Open Issues: {open_issues}\n"
    message += f"- Subscribers: {subscribers_count}"
    return f"[green]{message}"


def commit_in_last_year(commits_url: str, headers: dict) -> str:
    """
    11. Has there been a commit in the last year?
    """
    r = requests.get(commits_url, headers=headers).json()
    last_commit_date = r.get("commit").get("author").get("date")
    last_commit_date = datetime.strptime(last_commit_date, "%Y-%m-%dT%H:%M:%SZ")
    days_since_last_commit = (datetime.utcnow() - last_commit_date).days
    if days_since_last_commit > 365:
        message = f"[red]No. The last commit was {days_since_last_commit} days ago"
    else:
        message = f"[green]Yes. The last commit was on {datetime.strftime(last_commit_date, '%m-%d-%Y')} "
        message += f"which was {days_since_last_commit} days ago"

    return message


def release_in_last_year(pypi_api_url: str) -> str:
    """
    12. Has there been a release in the last year?
    """
    r = requests.get(pypi_api_url).json().get("releases")
    releases = _get_release_date(r)
    last_release_date = releases[0].upload_time
    version = releases[0].version
    last_release_date = datetime.strptime(last_release_date, "%Y-%m-%dT%H:%M:%S")
    days_since_last_release = (datetime.utcnow() - last_release_date).days
    if days_since_last_release > 365:
        message = f"[red]No. Version {version} was last released {days_since_last_release} days ago"
    else:
        message = f"[green]Yes. The last release was on {datetime.strftime(last_release_date, '%m-%d-%Y')}"
        message += f" which was {days_since_last_release} days ago"

    return message


def get_github_api_rate_limits(headers, resource):
    url = "https://api.github.com/rate_limit"
    response = requests.get(url, headers=headers).json()
    core = response.get("resources").get(resource)
    limit = core.get("limit")
    used = core.get("used")
    remaining = core.get("remaining")
    reset = strftime("%Y-%m-%d %H:%M:%S", localtime(core.get("reset")))
    message = f"You have used {used} out of {limit} calls.\n\n"
    message += f"You have {remaining} calls remaining.\n\n"
    message += f"Your limit will reset at {reset}."
    return message


def get_vulnerabilities(url: str) -> int:
    url = url
    vulnerabilities = requests.get(url).json().get("vulnerabilities")
    vulnerability_count = len(vulnerabilities)
    return vulnerability_count


def save_auth(auth: str) -> None:  # pragma: no cover
    # TODO: Write Test
    "Save authentication credentials to a JSON file"
    console.print("Create a GitHub personal user token and paste it here:")
    personal_token = Prompt.ask("Personal token")
    if Path(auth).exists():
        auth_data = json.load(open(auth))
    else:
        auth_data = {}
    auth_data["github_personal_token"] = personal_token
    open(auth, "w").write(json.dumps(auth_data, indent=4) + "\n")
