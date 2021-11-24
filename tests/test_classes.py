from datetime import datetime, timedelta
from random import randrange

today = datetime.now()
random_days_good = -randrange(25, 250)
random_days_bad = -randrange(400, 600)


GOOD_DATE = datetime.strftime(today + timedelta(days=random_days_good), "%Y-%m-%dT%H:%M:%SZ")
BAD_DATE = datetime.strftime(today + timedelta(days=random_days_bad), "%Y-%m-%dT%H:%M:%SZ")


class MockResponseCIPassing:
    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {"workflow_runs": [{"conclusion": "success"}]}


class MockResponseCIFailing:
    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {"workflow_runs": [{"conclusion": "fail"}]}


class MockResponseWellUsed:
    @staticmethod
    def json():
        return {
            "watchers": 5,
            "network_count": 6,
            "open_issues": 6,
            "subscribers_count": 10,
        }


class MockResponseCommitsYes:
    @staticmethod
    def json():
        return [{"commit": {"author": {"date": GOOD_DATE}}}]


class MockResponseCommitsNo:
    @staticmethod
    def json():
        return [{"commit": {"author": {"date": BAD_DATE}}}]


class MockResponseReleasesYes:
    @staticmethod
    def json():
        return [{"created_at": GOOD_DATE}]


class MockResponseReleasesNo:
    @staticmethod
    def json():
        return [{"created_at": BAD_DATE}]


class MockResponseCISetUpYes:
    @staticmethod
    def json():
        return {"total_count": 1, "workflows": [{"name": "Test"}]}


class MockResponseCISetUpNo:
    @staticmethod
    def json():
        return {"total_count": 0}


class MockResponseBugsYes:
    @staticmethod
    def json():
        return [
            {
                "id": 1,
                "node_id": ";lkjsdf",
                "url": "https://fakeurl",
                "event": "labeled",
                "commit_id": "null",
                "commit_url": "null",
                "created_at": "2019-07-14T00:00:00Z",
                "label": {"name": "bug", "color": "d73a4a"},
                "performed_via_github_app": "null",
            },
            {
                "id": 2,
                "node_id": "asdfsadf=",
                "url": "https://fakeurl",
                "event": "labeled",
                "commit_id": "null",
                "commit_url": "null",
                "created_at": "2019-07-14T00:00:00Z",
                "label": {"name": "help wanted", "color": "008672"},
                "performed_via_github_app": "null",
            },
            {
                "url": "https://fakeurl",
                "html_url": "https://fakeurl",
                "issue_url": "https://fakeurl",
                "id": 3,
                "node_id": "asdfs",
                "created_at": "2019-07-14T00:00:00Z",
                "updated_at": "2021-06-12T00:00:00Z",
                "author_association": "OWNER",
                "body": "This is the body.",
                "event": "commented",
            },
        ]


class MockResponseBugsNo:
    @staticmethod
    def json():
        return []


class MockResponseBugsWithNoResponse:
    @staticmethod
    def json():
        return [
            {
                "id": 1,
                "node_id": ";lkjsdf",
                "url": "https://fakeurl",
                "event": "labeled",
                "commit_id": "null",
                "commit_url": "null",
                "created_at": "2019-07-14T00:00:00Z",
                "label": {"name": "bug", "color": "d73a4a"},
                "performed_via_github_app": "null",
            },
        ]


class MockResponseProductionReadyYes:
    @staticmethod
    def json():
        return {"info": {"classifiers": ["Development Status :: 3 - Alpha"]}}


class MockResponseProductionReadyNo:
    @staticmethod
    def json():
        return {"info": {"classifiers": [], "version": "0.5"}}


class MockResponseDocumentationYes:
    @staticmethod
    def json():
        return {"info": {"project_urls": {"Documentation": "https://fakeurl/blob/main/README.md"}}}


class MockResponseDocumentationNo:
    @staticmethod
    def json():
        return {"info": {"project_urls": {}}}


class MockResponseLanguageCheck:
    @staticmethod
    def json():
        return {
            "info": {
                "classifiers": [
                    "Development Status :: 3 - Alpha",
                    "Intended Audience :: Developers",
                    "Intended Audience :: End Users/Desktop",
                    "Intended Audience :: Science/Research",
                    "License :: OSI Approved :: Apache Software License",
                    "Programming Language :: Python :: 3.6",
                    "Programming Language :: Python :: 3.7",
                    "Topic :: Database",
                ],
            }
        }


class MockResponseFrameworkCheck:
    @staticmethod
    def json():
        return {
            "info": {
                "classifiers": [
                    "Development Status :: 4 - Beta",
                    "Environment :: Web Environment",
                    "Framework :: Django",
                    "Framework :: Django :: 2.0",
                    "Framework :: Django :: 2.1",
                    "Framework :: Django :: 2.2",
                    "Framework :: Django :: 3.0",
                    "Framework :: Django :: 3.1",
                    "Framework :: Django :: 3.2",
                    "Intended Audience :: Developers",
                    "License :: OSI Approved :: MIT License",
                    "Operating System :: OS Independent",
                    "Programming Language :: Python",
                    "Programming Language :: Python :: 3",
                    "Programming Language :: Python :: 3.5",
                    "Programming Language :: Python :: 3.6",
                    "Programming Language :: Python :: 3.7",
                    "Programming Language :: Python :: 3.8",
                    "Programming Language :: Python :: 3.9",
                    "Topic :: Internet",
                    "Topic :: Software Development :: Libraries :: Python Modules",
                ],
                "version": "0.5",
            }
        }


class MockResponseCommentList:
    @staticmethod
    def json():
        return [
            {
                "created_at": "2019-07-14T00:00:00Z",
                "body": "This is the body.",
                "event": "commented",
            }
        ]


class MockGitHubFileCheckAPIWithTestFiles:
    @staticmethod
    def json():
        return {
            "sha": "98352ddf3a1ccffe8d38ecb34e1a51ed58d29cf3",
            "url": "https://api.github.com/repos/django/django/git/trees/98352ddf3a1ccffe8d38ecb34e1a51ed58d29cf3",
            "tree": [
                {
                    "path": ".editorconfig",
                    "mode": "100644",
                    "type": "blob",
                    "sha": "fa6c23c1fc276940d65520daedccc03d59b4b79c",
                    "size": 807,
                    "url": "https://api.github.com/repos/django/django/git/blobs/fa6c23c1fc276940d65520daedccc03d59b4b79c",
                },
                {
                    "path": ".eslintignore",
                    "mode": "100644",
                    "type": "blob",
                    "sha": "9c273ed532043fae2166ed38c281c510a841dccc",
                    "size": 120,
                    "url": "https://api.github.com/repos/django/django/git/blobs/9c273ed532043fae2166ed38c281c510a841dccc",
                },
                {
                    "path": "tests/admin_changelist/test_date_hierarchy.py",
                    "mode": "100644",
                    "type": "blob",
                    "sha": "a321650b32b0f3666d8470e9a69711756907f6ba",
                    "size": 3483,
                    "url": "https://api.github.com/repos/django/django/git/blobs/a321650b32b0f3666d8470e9a69711756907f6ba",
                },
            ],
        }


class MockGitHubFileCheckAPIWithOutTestFiles:
    @staticmethod
    def json():
        return {
            "sha": "98352ddf3a1ccffe8d38ecb34e1a51ed58d29cf3",
            "url": "https://api.github.com/repos/django/django/git/trees/98352ddf3a1ccffe8d38ecb34e1a51ed58d29cf3",
            "tree": [
                {
                    "path": ".editorconfig",
                    "mode": "100644",
                    "type": "blob",
                    "sha": "fa6c23c1fc276940d65520daedccc03d59b4b79c",
                    "size": 807,
                    "url": "https://api.github.com/repos/django/django/git/blobs/fa6c23c1fc276940d65520daedccc03d59b4b79c",
                },
                {
                    "path": ".eslintignore",
                    "mode": "100644",
                    "type": "blob",
                    "sha": "9c273ed532043fae2166ed38c281c510a841dccc",
                    "size": 120,
                    "url": "https://api.github.com/repos/django/django/git/blobs/9c273ed532043fae2166ed38c281c510a841dccc",
                },
            ],
        }
