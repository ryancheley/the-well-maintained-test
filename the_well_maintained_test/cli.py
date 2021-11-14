from collections import namedtuple
from datetime import datetime, time
import json
from operator import attrgetter
from urllib.parse import urlparse

import click
from click.types import Choice
import requests
from rich import print
from .utils import (
    yes_no, 
    change_log_check, 
    bug_responding, 
    ci_setup, 
    ci_passing, 
    well_used,
    commit_in_last_year,
    release_in_last_year
)


@click.command()
@click.version_option()
@click.argument("url")
@click.option('--username' ,help='What GitHub Username you use')
def cli(url, username):
    """
    Programatically tries to answer the 12 questions from Adam Johnson's blog post https://adamj.eu/tech/2021/11/04/the-well-maintained-test/

    URL is a url to a github repository you'd like to check, for example:

        the-well-maintained-test 'https://github.com/ryancheley/the-well-maintained-test'

    """
    if username:
        auth=(username, '')
    else:
        auth=()
    if url[-1] == '/':
        url = url.strip('/')

    parse_object = urlparse(url)
    author = parse_object.path.split('/')[-2]
    package = parse_object.path.split('/')[-1]
    api_url = f'https://api.github.com/repos/{author}/{package}'
    changelog_url = f'https://raw.githubusercontent.com/{author}/{package}/main/CHANGELOG.md'
    releases_url = f'https://www.github.com/{author}/{package}/releases'
    releases_api_url = f'https://api.github.com/repos/{author}/{package}/releases'
    commits_url = f'https://api.github.com/repos/{author}/{package}/commits'
    workflows_url = f'https://api.github.com/repos/{author}/{package}/actions/workflows'
    ci_status_url = f'https://api.github.com/repos/{author}/{package}/actions/runs'
    bugs_url = f'https://api.github.com/repos/{author}/{package}/issues?labels=bug'
    changelog = requests.get(changelog_url, auth=auth)
    release = requests.get(releases_url, auth=auth)

    print(yes_no("1. Is it described as 'production ready'?"))

    print(yes_no("2. Is there sufficient documentation?"))

    print(change_log_check(changelog, release))

    print(bug_responding(bugs_url, auth))

    print(yes_no("5. Are there sufficient tests?"))

    print(yes_no("6. Are the tests running with the latest Language version?"))

    print(yes_no("7. Are the tests running with the latest Integration version?"))

    print(ci_setup(workflows_url, auth))

    print(ci_passing(ci_status_url, auth))

    print(well_used(api_url, auth))

    print(commit_in_last_year(commits_url, auth))

    print(release_in_last_year(releases_api_url, auth))