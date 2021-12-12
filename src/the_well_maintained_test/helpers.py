import base64
import re
from collections import namedtuple
from datetime import datetime
from operator import attrgetter
from pathlib import Path
from typing import List
from urllib.parse import urlparse

import requests


def _get_bug_comment_list(url: str, headers: dict) -> list:
    BugComments = namedtuple("BugComments", ["text", "create_date"])
    bug_comment_list = []
    timeline = requests.get(url, headers=headers).json()
    for t in timeline:
        if t.get("event") == "commented":
            bug_comment = t.get("body")
            bug_comment_date = datetime.strptime(t.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
            bug_comment_list.append(BugComments(bug_comment, bug_comment_date))
    return bug_comment_list


def _get_content(url: str, headers: dict) -> bytes:
    response = requests.get(url, headers=headers).json()
    if response.get("encoding") != "base64":
        raise TypeError
    else:
        content = response.get("content")
    return content


def _test_method_count(content: bytes) -> int:
    content_list = str(base64.b64decode(content)).split("\\n")
    test_methods = [s for s in content_list if "test_" in s]
    return len(test_methods)


def _get_test_files(url: str, headers: dict) -> list:
    test_file_list = []
    r = requests.get(url, headers=headers).json()
    for i in r.get("tree"):
        if i.get("type") == "blob" and re.search(r"test(s|_(.*)).py", i.get("path")):
            test_file_list.append(i)

    return test_file_list


def _get_release_date(release: dict) -> List:
    Release = namedtuple("Release", "version, upload_time")
    releases = []
    for k, v in release.items():
        if not re.search(r"[a-zA-Z]", k):
            try:
                releases.append(Release(k, v[0].get("upload_time")))
            except IndexError:
                pass
    releases = sorted(releases, key=attrgetter("upload_time"), reverse=True)
    return releases


def _get_requirements_txt_file(requirements_file: Path) -> List:
    with open(requirements_file) as f:
        requirements = f.readlines()
    packages = [s.replace("\n", "").replace("==", " ").split(" ")[0] for s in requirements]
    package_urls = []
    for package in packages:
        data = _get_package_github_url(package)
        package_urls.append(data)
    return sorted(package_urls, key=lambda x: x[0].lower())


def _get_package_github_url(package: str) -> tuple:
    url = f"https://pypi.org/pypi/{package}/json"
    project_urls = requests.get(url).json().get("info").get("project_urls")
    for k, v in project_urls.items():
        if urlparse(v).netloc == "github.com" and len(urlparse(v).path.split("/")) == 3:
            value = (package, v)
        elif urlparse(v).netloc == "github.com" and len(urlparse(v).path.split("/")) == 4:
            p = urlparse(v).path.split("/")[1]
            a = urlparse(v).path.split("/")[2]
            value = (package, f"https://www.github.com/{p}/{a}")
    return value
