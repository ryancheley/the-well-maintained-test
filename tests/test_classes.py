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


class MockResponseBugsYes:
    @staticmethod
    def json():
        return [{
            "created_at": GOOD_DATE,"number": 0,"timeline_url": "test"
        }]


class MockResponseBugsNo:
    @staticmethod
    def json():
        return {}


class MockResponseProductionReadyYes:
    @staticmethod
    def json():
        return [{"name": "1.0"}]


class MockResponseProductionReadyNoAlpha:
    @staticmethod
    def json():
        return [{"name": "1.0a"}]


class MockResponseProductionReadyNoBeta:
    @staticmethod
    def json():
        return [{"name": "1.0b"}]


class MockResponseProductionReadyNoOther:
    @staticmethod
    def json():
        return [{"name": "1.0c"}]
