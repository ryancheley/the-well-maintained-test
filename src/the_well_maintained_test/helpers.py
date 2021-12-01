import base64
import re
from collections import namedtuple
from datetime import datetime
from operator import attrgetter
from typing import List

import requests


def _get_bug_comment_list(url: str, headers: dict) -> list:
    BugComments = namedtuple("BugComments", ["text", "create_date"])
    bug_comment_list = []
    timeline = requests.get(url, headers=headers).json()[-1]
    if timeline.get("event") == "commented":
        bug_comment = timeline.get("body")
        bug_comment_date = datetime.strptime(timeline.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
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
        if i.get("type") == "blob" and re.search(r"test_(.*).py", i.get("path")):
            test_file_list.append(i)

    return test_file_list


def _get_release_date(release: dict) -> List:
    Release = namedtuple("Release", "version, upload_time")
    releases = []
    for k, v in release.items():
        if not re.search(r"[a-zA-Z]", k):
            releases.append(Release(k, v[0].get("upload_time")))
    releases = sorted(releases, key=attrgetter("upload_time"), reverse=True)
    return releases


def _check_verb_agreement(count: int) -> str:
    if count == 1:
        verb = "is"
    else:
        verb = "are"
    return verb
