from collections import namedtuple
from datetime import datetime, time
import json
from operator import attrgetter
from urllib.parse import urlparse

import requests
from rich.prompt import Confirm
from rich import print


def yes_no(question):
    answer = Confirm.ask(question)
    if answer:
        return "[bold green]\tYes[bold]"
    else:
        return "[bold red]\tNo[bold]"
    
def change_log_check(changelog, release):
    print("3. Is there a changelog?")
    if changelog.status_code == 200 or release.status_code == 200:
        return "[bold green]\tYes[bold]"
    else:
        return "[bold red]\tNo[bold]"


def bug_responding(bugs_url, auth):
    print("4. Is someone responding to bug reports?")
    BugComments = namedtuple('BugComments', ['text', 'create_date', 'bug_id'])
    r = requests.get(bugs_url, auth=auth).json()
    bug_comment_list = []
    for i in r:
        bug_create_date = datetime.strptime(i.get('created_at'), '%Y-%m-%dT%H:%M:%SZ')
        bug_text = i.get('body')
        bug_id = i.get('number')
        timeline = requests.get(i.get('timeline_url'), auth=auth).json()
        for item in timeline:
            if item.get('event') == "commented":
                bug_comment = item.get('body')
                bug_comment_date = datetime.strptime(item.get('created_at'), '%Y-%m-%dT%H:%M:%SZ')
                bug_comment_list.append(BugComments(bug_comment, bug_comment_date, bug_id))
    bug_comment_list = sorted(bug_comment_list, key=attrgetter('create_date'), reverse=True)
    if bug_comment_list:
        bug_turn_around_time_reply_days = (bug_comment_list[0].create_date - bug_create_date).days
        days_since_last_bug_comment = (datetime.today() - bug_comment_list[0].create_date).days
        # TODO: add logic to better colorize the message
        message1 = f"The maintainer took {bug_turn_around_time_reply_days} days to respond to the bug report {bug_comment_list[0].bug_id}"
        message2 = f"It has been {days_since_last_bug_comment} days since a comment was made on the bug."
        message = f"""[bold red]\t{message1}\n\t{message2}[bold]
        """
        return message
    else:
        return "\t[bold green]There have been no bugs reported that are still open.[bold]"
        


def ci_setup(workflows_url, auth):
    print("8. Is there a Continuous Integration (CI) configuration?")
    r = requests.get(workflows_url, auth=auth).json()
    if r.get('total_count') > 0:
        message = f"[bold green]\tThere are {r.get('total_count')} workflows[bold]\n"
        for i in r.get('workflows'):
            message += f"[bold blue]\t - {i.get('name')}\n[bold]"
        return message
    else:
        return "[bold red]There is no CI set up![bold]"
        


def ci_passing(ci_status_url, auth):
    print("[bold]9. Is the CI passing?")
    r = requests.get(ci_status_url, auth=auth).json()
    conclusion = r.get('workflow_runs')[0].get('conclusion')
    if conclusion == "success":
        return "\t[green]Yes"
    else:
        return "\t[red]No"


def well_used(api_url, auth):
    print("[bold]10. Does it seem relatively well used?")

    r = requests.get(api_url, auth=auth).json()
    watchers = r.get('watchers')
    network_count = r.get('network_count')
    open_issues = r.get('open_issues')
    subscribers_count = r.get('subscribers_count')
    message = "\tThe project has the following statistics:\n"
    message += f"\t- Watchers: {watchers}\n"
    message += f"\t- Forks: {network_count}\n"
    message += f"\t- Open Issues: {open_issues}\n"
    message += f"\t- Subscribers: {subscribers_count}"
    return message


def commit_in_last_year(commits_url, auth):
    print("[bold]11. Has there been a commit in the last year?")
    r = requests.get(commits_url, auth=auth).json()
    last_commit_date = r[0].get('commit').get('author').get('date')
    last_commit_date = datetime.strptime(last_commit_date, '%Y-%m-%dT%H:%M:%SZ')
    days_since_last_commit = (datetime.today() - last_commit_date).days
    if days_since_last_commit > 365:
        message = f"\t[red]No. The last commit was {days_since_last_commit} days ago"
    else:
        message = f"\t[green]Yes. The last commit was on {datetime.strftime(last_commit_date, '%m-%d-%Y')} which was {days_since_last_commit} days ago"

    return message


def release_in_last_year(releases_api_url, auth):
    print("[bold]12. Has there been a release in the last year?")
    r = requests.get(releases_api_url, auth=auth).json()
    last_release_date = r[0].get('created_at')
    last_release_date = datetime.strptime(last_release_date, '%Y-%m-%dT%H:%M:%SZ')
    days_since_last_release = (datetime.today() - last_release_date).days
    if days_since_last_release > 365:
        message = f"\t[red]No. The last commit was {days_since_last_release} days ago"
    else:
        message = f"\t[green]Yes. The last commit was on {datetime.strftime(last_release_date, '%m-%d-%Y')} which was {days_since_last_release} days ago"

    return message
