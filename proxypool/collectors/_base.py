import re
import time
import random
from datetime import datetime, timedelta
from abc import ABC
from contextlib import contextmanager
try:
    import simplejson as json
except ImportError:
    import json

from lxml import html as HTMLParser
import requests
from requests.exceptions import RequestException


class ProxyRecord:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ip = kwargs.get('ip', '')
        self.port = kwargs.get('port', '')
        self.type = kwargs.get('type', '')
        self.anonymity = kwargs.get('anonymity', '')
        self.speed = kwargs.get('speed', '')
        self.country = kwargs.get('country', '')
        self.score = kwargs.get('score', '')

    def __repr__(self):
        return '<ProxyRecord {}:{}, {}>'.format(
            self.ip, self.port, self.type
        )

    __str__ = __repr__


@contextmanager
def _get_requests_session(*args, **kwargs):
    try:
        with requests.Session() as ses:
            ses.headers.update({
                'User-Agent': (
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                    ' (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
                )
            })
            yield ses
    except Exception:
        pass


def _send_request(ses, url, retry=5, sleep=30, timeout=120, *args, **kwargs):
    for retry_idx in range(retry):
        try:
            res = ses.get(url, timeout=timeout)
            if res.status_code != 200:
                raise RequestException(
                    'Response not OK for {}'.format(url)
                )
            return res
        except RequestException:
            if retry_idx == retry - 1:
                raise
            time.sleep(retry_idx * sleep + random.random() * sleep)
        except Exception:
            raise


class BaseProxyDataCollector(ABC):
    def __init__(self, retry=5, sleep=30, timeout=120, *args, **kwargs):
        self.retry = retry
        self.sleep = sleep
        self.timeout = timeout
        self.url = None

    def get_data(self):
        res = None
        with _get_requests_session() as ses:
            res = _send_request(
                ses, self.url, self.retry, self.sleep, self.timeout
            )
        yield from self.parse_response(res)

    def parse_response(self, res, **kwargs):
        if res is None:
            raise StopIteration
