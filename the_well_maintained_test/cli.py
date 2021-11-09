from collections import namedtuple
from datetime import datetime, time
import json
from operator import attrgetter
from urllib.parse import urlparse

import click
from click.types import Choice
import requests


@click.command()
@click.version_option()
@click.argument("url")
def cli(url):
    """
    Programatically tries to answer the 12 questions from Adam Johnson's blog post https://adamj.eu/tech/2021/11/04/the-well-maintained-test/
    """
    parse_object = urlparse(url)
    author = parse_object.path.split('/')[-2]
    package = parse_object.path.split('/')[-1]
    changelog_url = f'https://raw.githubusercontent.com/{author}/{package}/main/CHANGELOG.md'
    releases_url = f'https://api.github.com/{author}/{package}/releases'
    releases_api_url = f'https://api.github.com/repos/{author}/{package}/releases'
    commits_url = f'https://api.github.com/repos/{author}/{package}/commits'
    workflows_url = f'https://api.github.com/repos/{author}/{package}/actions/workflows'
    ci_status_url = f'https://api.github.com/repos/{author}/{package}/actions/runs'
    bugs_url = f'https://api.github.com/repos/{author}/{package}/issues?labels=bug'
    changelog = requests.get(changelog_url)
    release = requests.get(releases_url)

    answer_1 = click.prompt("1. Is it described as 'production ready'?", type=Choice(choices=['Yes','No']), show_choices=True)
    click.echo(f"\t{answer_1}")

    answer_2 = click.prompt("2. Is there sufficient documentation?", type=Choice(choices=['Yes','No']), show_choices=True)
    click.echo(f"\t{answer_2}")

    click.echo("3. Is there a changelog?")
    if changelog.status_code == 200 or release.status_code == 200:
        click.echo("\tYes")
    else:
        click.echo("\tNo")

    click.echo("4. Is someone responding to bug reports?")
    BugComments = namedtuple('BugComments', ['text', 'create_date', 'bug_id'])
    r = requests.get(bugs_url).json()
    bug_comment_list = []
    for i in r:
        bug_create_date = datetime.strptime(i.get('created_at'), '%Y-%m-%dT%H:%M:%SZ')
        bug_text = i.get('body')
        bug_id = i.get('number')
        timeline = requests.get(i.get('timeline_url')).json()
        for item in timeline:
            if item.get('event') == "commented":
                bug_comment = item.get('body')
                bug_comment_date = datetime.strptime(item.get('created_at'), '%Y-%m-%dT%H:%M:%SZ')
                bug_comment_list.append(BugComments(bug_comment, bug_comment_date, bug_id))
    bug_comment_list = sorted(bug_comment_list, key=attrgetter('create_date'), reverse=True)
    if bug_comment_list:
        bug_turn_around_time_reply_days = (bug_comment_list[0].create_date - bug_create_date).days
        days_since_last_bug_comment = (datetime.today() - bug_comment_list[0].create_date).days
        message1 = f"The maintainer took {bug_turn_around_time_reply_days} days to respond to the bug report {bug_comment_list[0].bug_id}"
        message2 = f"It has been {days_since_last_bug_comment} days since a comment was made on the bug."
        click.echo(f"\t{message1}")
        click.echo(f"\t{message2}")
    else:
        click.echo("\tThere have been no bugs reported that are still open.")


    answer_5 = click.prompt("5. Are there sufficient tests?", type=Choice(choices=['Yes','No']), show_choices=True)
    click.echo(f"\t{answer_5}")

    answer_6 = click.prompt("6. Are the tests running with the latest Language version?", type=Choice(choices=['Yes','No']), show_choices=True)
    click.echo(f"\t{answer_6}")

    answer_7 = click.prompt("7. Are the tests running with the latest Integration version?", type=Choice(choices=['Yes','No']), show_choices=True)
    click.echo(f"\t{answer_7}")

    click.echo("8. Is there a Continuous Integration (CI) configuration?")
    r = requests.get(workflows_url).json()
    if r.get('total_count') > 0:
        click.echo(f"\tThere are {r.get('total_count')} workflows")
        for i in r.get('workflows'):
            click.echo(f"\t\t- {i.get('name')}")
    else:
        click.echo("There is no CI set up!")
    

    click.echo("9. Is the CI passing?")
    r = requests.get(ci_status_url).json()
    conclusion = r.get('workflow_runs')[0].get('conclusion')
    if conclusion == "success":
        click.echo("\tYes")
    else:
        click.echo("\tNo")


    click.echo("10. Does it seem relatively well used?")

    r = requests.get(url).json()
    watchers = r.get('watchers')
    network_count = r.get('network_count')
    open_issues = r.get('open_issues')
    subscribers_count = r.get('subscribers_count')
    click.echo("\tThe project has the following statistics:")
    click.echo(f"\t\tWatchers: {watchers}")
    click.echo(f"\t\tForks: {network_count}")
    click.echo(f"\t\tOpen Issues: {open_issues}")
    click.echo(f"\t\tSubscribers: {subscribers_count}")     

    click.echo("11. Has there been a commit in the last year?")
    r = requests.get(commits_url).json()
    last_commit_date = r[0].get('commit').get('author').get('date')
    last_commit_date = datetime.strptime(last_commit_date, '%Y-%m-%dT%H:%M:%SZ')
    days_since_last_commit = (datetime.today() - last_commit_date).days
    if days_since_last_commit > 365:
        click.echo(f"\tNo. The last commit was {days_since_last_commit} days ago")
    else:
        click.echo(f"\tYes. The last commit was on {datetime.strftime(last_commit_date, '%m-%d-%Y')} which was {days_since_last_commit} days ago")

    click.echo("12. Has there been a release in the last year?")
    r = requests.get(releases_api_url).json()
    last_release_date = r[0].get('created_at')
    last_release_date = datetime.strptime(last_release_date, '%Y-%m-%dT%H:%M:%SZ')
    days_since_last_release = (datetime.today() - last_release_date).days
    if days_since_last_release > 365:
        click.echo(f"\tNo. The last commit was {days_since_last_release} days ago")
    else:
        click.echo(f"\tYes. The last commit was on {datetime.strftime(last_release_date, '%m-%d-%Y')} which was {days_since_last_release} days ago")
