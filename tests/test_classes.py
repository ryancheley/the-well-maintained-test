from datetime import datetime, timedelta
from random import randrange

today = datetime.now()
random_days_good = -randrange(25, 250)
random_days_bad = -randrange(400, 600)


GOOD_DATE = datetime.strftime(today + timedelta(days=random_days_good), "%Y-%m-%dT%H:%M:%S")
GOOD_DATE_Z = datetime.strftime(today + timedelta(days=random_days_good), "%Y-%m-%dT%H:%M:%SZ")
BAD_DATE = datetime.strftime(today + timedelta(days=random_days_bad), "%Y-%m-%dT%H:%M:%S")
BAD_DATE_Z = datetime.strftime(today + timedelta(days=random_days_bad), "%Y-%m-%dT%H:%M:%SZ")


class MockResponseCIPassing:
    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {"workflow_runs": [{"conclusion": "success"}]}


class MockResponseCINoConclusion:
    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {"workflow_runs": []}


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
        return {"commit": {"author": {"date": GOOD_DATE_Z}}}


class MockResponseCommitsNo:
    @staticmethod
    def json():
        return {"commit": {"author": {"date": BAD_DATE_Z}}}


class MockResponseReleasesYes:
    @staticmethod
    def json():
        return {
            "releases": {
                "1.1.1": [{"upload_time": GOOD_DATE}],
                "1.1.1a": [{"upload_time": GOOD_DATE}],
            }
        }


class MockResponseReleasesNo:
    @staticmethod
    def json():
        return {"releases": {"1.1.1": [{"upload_time": BAD_DATE}]}}


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


class MockResponseContentBase64:
    @staticmethod
    def json():
        return {"encoding": "base64", "content": "test"}


class MockResponseContentNotBase64:
    @staticmethod
    def json():
        return {"encoding": "notbase64"}


class MockResponseTestFilesExist:
    @staticmethod
    def json():
        return {
            "tree": [
                {
                    "type": "blob",
                    "path": "tests/test_management.py",
                },
                {
                    "path": "friendship/tests/tests.py",
                    "type": "blob",
                },
            ]
        }


class MockResponseTestFilesDoNotExist:
    @staticmethod
    def json():
        return {
            "tree": [
                {
                    "type": "blob",
                    "path": "requirements/py38-django40.txt",
                }
            ]
        }


class MockResponseTestFilesNoBlobs:
    @staticmethod
    def json():
        return {"tree": [{"type": "tree"}]}


class MockResponseProjectURLs:
    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {
            "info": {
                "project_urls": {
                    "Documentation": "https://docs.djangoproject.com/",
                    "Funding": "https://www.djangoproject.com/fundraising/",
                    "Homepage": "https://www.djangoproject.com/",
                    "Release notes": "https://docs.djangoproject.com/en/stable/releases/",
                    "Source": "https://github.com/django/django",
                    "Tracker": "https://code.djangoproject.com/",
                }
            }
        }


class MockResponseGitHubRateLimit:
    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {
            "resources": {
                "core": {"limit": 5000, "remaining": 4999, "reset": 1372700873, "used": 1},
                "search": {"limit": 30, "remaining": 18, "reset": 1372697452, "used": 12},
                "graphql": {"limit": 5000, "remaining": 4993, "reset": 1372700389, "used": 7},
                "integration_manifest": {"limit": 5000, "remaining": 4999, "reset": 1551806725, "used": 1},
                "code_scanning_upload": {"limit": 500, "remaining": 499, "reset": 1551806725, "used": 1},
            },
            "rate": {"limit": 5000, "remaining": 4999, "reset": 1372700873, "used": 1},
        }


class MockResponseWithVulnerabilities:
    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {
            "vulnerabilities": [
                {
                    "aliases": ["CVE-2014-0472"],
                    "details": "details",
                    "fixed_in": ["1.4.11", "1.5.6", "1.6.3"],
                    "id": "PYSEC-2014-1",
                    "link": "https://osv.dev/vulnerability/PYSEC-2014-1",
                    "source": "osv",
                },
                {
                    "aliases": ["CVE-2011-4136"],
                    "details": "details",
                    "fixed_in": ["1.2.7", "1.3.1"],
                    "id": "PYSEC-2011-1",
                    "link": "https://osv.dev/vulnerability/PYSEC-2011-1",
                    "source": "osv",
                },
                {
                    "aliases": ["CVE-2011-4140"],
                    "details": "details",
                    "fixed_in": ["1.2.7", "1.3.1"],
                    "id": "PYSEC-2011-5",
                    "link": "https://osv.dev/vulnerability/PYSEC-2011-5",
                    "source": "osv",
                },
            ]
        }


class MockResponseWithoutVulnerabilities:
    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {"vulnerabilities": []}


class MockResponseChangelogYes:
    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {
            "info": {
                "project_urls": {
                    "Changelog": "https://github.com/ryancheley/the-well-maintained-test/releases",
                }
            }
        }


class MockResponseChangelogNo:
    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {
            "info": {
                "project_urls": {
                    "Home Page": "https://github.com/ryancheley/the-well-maintained-test/releases",
                }
            }
        }


class MockResponseNonGitHubHomePage:
    @staticmethod
    def json():
        return {
            "info": {
                "project_urls": {
                    "CI": "https://github.com/author/package/actions",
                    "Changelog": "https://github.com/author/package/releases",
                    "Homepage": "https://www.package.com",
                    "Issues": "https://github.com/author/package/issues",
                }
            }
        }
