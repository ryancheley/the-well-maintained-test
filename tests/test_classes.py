from datetime import datetime, timedelta
from random import randrange

today = datetime.now()
random_days_good = -randrange(25, 250)
random_days_bad = -randrange(400, 600)


GOOD_DATE = datetime.strftime(today + timedelta(days=random_days_good), '%Y-%m-%dT%H:%M:%SZ')
BAD_DATE = datetime.strftime(today + timedelta(days=random_days_bad), '%Y-%m-%dT%H:%M:%SZ')


class MockResponseCIPassing:
    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {"workflow_runs": [{
            "conclusion": "success"
        }]}


class MockResponseCIFailing:
    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {"workflow_runs": [{
            "conclusion": "fail"
        }]}

class MockResponseWellUsed:
    @staticmethod
    def json():
        return {
            "watchers": 5,
            "network_count": 6,
            "open_issues": 6,
            "subscribers_count": 10
        }



class MockResponseCommitsYes:
    @staticmethod
    def json():
        return [{
            "commit": {
                "author": {
                    "date": GOOD_DATE
                }
            }
        }]


class MockResponseCommitsNo:
    @staticmethod
    def json():
        return [{
            "commit": {
                "author": {
                    "date": BAD_DATE
                }
            }
        }]


class MockResponseReleasesYes:
    @staticmethod
    def json():
        return [{
            "created_at": GOOD_DATE
        }]


class MockResponseReleasesNo:
    @staticmethod
    def json():
        return [{
            "created_at": BAD_DATE
        }]


class MockResponseCISetUpYes:
    @staticmethod
    def json():
        return {
            "total_count": 1,
            "workflows": [
                {
                    "name": "Test"
                }
            ]
        }


class MockResponseCISetUpNo:
    @staticmethod
    def json():
        return {
            "total_count": 0
        }


class MockResponseBugsNo:
    @staticmethod
    def json():
        return {}

class MockResponseProductionReadyYes:
    @staticmethod
    def json():
        return {
            "info": {
                "classifiers": [
                    'Development Status :: 3 - Alpha'
                ]
                }
            }

class MockResponseProductionReadyNo:
    @staticmethod
    def json():
        return {
            "info": {
                "classifiers": [],
                "version": "0.5"
            }
            }


class MockResponseDocumentationYes:
    @staticmethod
    def json():
        return {
            "info": {
                "project_urls": {
                    "Documentation": "https://github.com/simonw/db-to-sqlite/blob/main/README.md"
                }
            }
            }


class MockResponseDocumentationNo:
    @staticmethod
    def json():
        return {
            "info": {
                "project_urls": {
                    
                }
            }
            }


class MockResponseLanguageCheck:
    @staticmethod
    def json():
        return {
            "info": {
                "classifiers": ["Development Status :: 3 - Alpha","Intended Audience :: Developers","Intended Audience :: End Users/Desktop","Intended Audience :: Science/Research","License :: OSI Approved :: Apache Software License","Programming Language :: Python :: 3.6","Programming Language :: Python :: 3.7","Topic :: Database"],
            }
            }


class MockResponseFrameworkCheck:
    @staticmethod
    def json():
        return {
            "info": {
                "classifiers": ["Development Status :: 4 - Beta","Environment :: Web Environment","Framework :: Django","Framework :: Django :: 2.0","Framework :: Django :: 2.1","Framework :: Django :: 2.2","Framework :: Django :: 3.0","Framework :: Django :: 3.1","Framework :: Django :: 3.2","Intended Audience :: Developers","License :: OSI Approved :: MIT License","Operating System :: OS Independent","Programming Language :: Python","Programming Language :: Python :: 3","Programming Language :: Python :: 3.5","Programming Language :: Python :: 3.6","Programming Language :: Python :: 3.7","Programming Language :: Python :: 3.8","Programming Language :: Python :: 3.9","Topic :: Internet","Topic :: Software Development :: Libraries :: Python Modules"],
                "version": "0.5"
            }
            }

