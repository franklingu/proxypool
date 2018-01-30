"""Collectors to crawl free IP proxies from the internet
"""
import re
import time
import random
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
        return 'ProxyRecord<{}:{}, {}, {}>'.format(
            self.ip, self.port, self.type, self.country
        )


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


def feilong_collector(retry=5, sleep=30, *args, **kwargs):
    url = 'http://www.feilongip.com/'
    sel = '#j-tab-newprd > table.FreeIptable > tbody.FreeIptbody > tr'
    patt = r'(\d+\.\d+\.\d+\.\d+):(\d+)'
    with _get_requests_session() as ses:
        for retry_idx in range(retry):
            try:
                res = ses.get(url, timeout=sleep)
                if res.status_code != 200:
                    raise RequestException(
                        'Response not OK for {}'.format(url)
                    )
                parsed = HTMLParser.fromstring(res.content)
                for tr_elem in parsed.cssselect(sel):
                    tds = tr_elem.cssselect('td')
                    if len(tds) != 8:
                        continue
                    match = re.match(patt, tds[1].text.strip())
                    if not match:
                        continue
                    ip = match.group(1)
                    port = match.group(2)
                    server_type = (''.join(tds[4].itertext())).strip()
                    rec = ProxyRecord()
                    rec.ip = ip
                    rec.port = port
                    rec.type = server_type
                    yield rec
                break
            except (RequestException, IndexError):
                if retry_idx == retry - 1:
                    raise
                time.sleep(retry_idx * sleep + random.random() * sleep)
            except Exception:
                raise
