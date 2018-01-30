"""Collectors to crawl free IP proxies from the internet
"""
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


class FeilongProxyDataCollector(BaseProxyDataCollector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'http://www.feilongip.com/'

    def parse_response(self, res, **kwargs):
        super().parse_response(res)
        parsed = HTMLParser.fromstring(res.content)
        patt = r'(\d+\.\d+\.\d+\.\d+):(\d+)'
        sel = '#j-tab-newprd > table.FreeIptable > tbody.FreeIptbody > tr'
        for tr_elem in parsed.cssselect(sel):
            tds = tr_elem.cssselect('td')
            if len(tds) != 8:
                continue
            match = re.match(patt, tds[1].text.strip())
            if not match:
                continue
            ip = match.group(1)
            port = match.group(2)
            server_type = (''.join(tds[4].itertext())).strip().lower()
            rec = ProxyRecord()
            rec.ip = ip
            rec.port = port
            rec.type = server_type
            yield rec


class WuyouProxyDataCollector(BaseProxyDataCollector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.urls = [
            'http://www.data5u.com/free/index.shtml',
            'http://www.data5u.com/free/gngn/index.shtml',
            'http://www.data5u.com/free/gnpt/index.shtml',
            'http://www.data5u.com/free/gwgn/index.shtml',
            'http://www.data5u.com/free/gwpt/index.shtml',
        ]

    def get_data(self):
        with _get_requests_session() as ses:
            for url in self.urls:
                res = None
                res = _send_request(
                    ses, url, self.retry, self.sleep, self.timeout
                )
                if res is None:
                    continue
                parsed = HTMLParser.fromstring(res.content)
                sel = 'div.wlist > ul > li > ul.l2'
                for ul_elem in parsed.cssselect(sel):
                    lis = ul_elem.cssselect('span > li')
                    if len(lis) != 9:
                        continue
                    rec = ProxyRecord()
                    rec.ip = lis[0].text.strip()
                    rec.port = lis[1].text.strip()
                    rec.type = (''.join(lis[3].itertext())).strip().lower()
                    yield rec


class XiciProxyDataCollector(BaseProxyDataCollector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'http://www.xicidaili.com/nn'
        self.back_limit = timedelta(hours=1)
        if 'back_limit' in kwargs:
            self.back_limit = timedelta(hours=int(kwargs['back_limit']))

    def get_data(self):
        with _get_requests_session() as ses:
            url = self.url
            while url is not None:
                res = None
                res = _send_request(
                    ses, url, self.retry, self.sleep, self.timeout
                )
                print(url)
                if res is None:
                    url = None
                    continue
                parsed = HTMLParser.fromstring(res.content)
                sel = 'table#ip_list tr'
                for ul_elem in parsed.cssselect(sel):
                    tds = ul_elem.cssselect('td')
                    if len(tds) != 10:
                        continue
                    try:
                        dt = datetime.strptime(tds[-1].text, '%y-%m-%d %H:%M')
                    except ValueError:
                        url = None
                        break
                    dt = dt + timedelta(hours=-8)
                    if datetime.utcnow() - dt > self.back_limit:
                        url = None
                        break
                    rec = ProxyRecord()
                    rec.ip = tds[1].text.strip()
                    rec.port = tds[2].text.strip()
                    rec.type = tds[5].text.strip().lower()
                    yield rec
                if url is None:
                    break
                try:
                    url = 'http://www.xicidaili.com{}'.format(
                        parsed.cssselect('a.next_page')[0].get('href')
                    )
                except IndexError:
                    url = None


class IP181ProxyDataCollector(BaseProxyDataCollector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'http://www.ip181.com/daili/1.html'
        self.back_limit = timedelta(hours=12)
        if 'back_limit' in kwargs:
            self.back_limit = timedelta(hours=int(kwargs['back_limit']))

    def get_data(self):
        with _get_requests_session() as ses:
            url = self.url
            while url is not None:
                res = None
                res = _send_request(
                    ses, url, self.retry, self.sleep, self.timeout
                )
                if res is None:
                    url = None
                    continue
                parsed = HTMLParser.fromstring(res.content)
                sel = (
                    'table.table.table-hover.panel-default.panel.ctable'
                    ' > tbody > tr'
                )
                for tr_elem in parsed.cssselect(sel):
                    tds = tr_elem.cssselect('td')
                    if len(tds) != 7:
                        continue
                    if 'IP' in tds[0].text:
                        continue
                    try:
                        dt = datetime.strptime(
                            tds[-1].text, '%Y/%m/%d %H:%M:%S'
                        )
                    except ValueError:
                        url = None
                        break
                    dt = dt + timedelta(hours=-8)
                    if datetime.utcnow() - dt > self.back_limit:
                        url = None
                        break
                    rec = ProxyRecord()
                    rec.ip = tds[0].text.strip()
                    rec.port = tds[1].text.strip()
                    rec.type = tds[3].text.strip().lower()
                    yield rec
                if url is None:
                    break
                try:
                    url = 'http://www.ip181.com/{}'.format(
                        parsed.cssselect('a[title=下一页]')[0].get('href')
                    )
                except IndexError:
                    url = None


class CNProxyDataCollector(BaseProxyDataCollector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'http://cn-proxy.com/'
        self.addon_url = None

    def get_data(self):
        res = None
        with _get_requests_session() as ses:
            res = _send_request(
                ses, self.url, self.retry, self.sleep, self.timeout
            )
            yield from self.parse_response(res)
            if self.addon_url:
                res = _send_request(
                    ses, self.addon_url, self.retry, self.sleep, self.timeout
                )
                yield from self.parse_archive_response(res)

    def parse_response(self, res, **kwargs):
        super().parse_response(res)
        parsed = HTMLParser.fromstring(res.content)
        if self.addon_url is None:
            try:
                self.addon_url = parsed.xpath(
                    '//a[text()="全球范围代理服务器"]'
                )[0].get('href')
            except IndexError:
                pass
        sel = 'div.table-container > table.sortable > tbody > tr'
        for tr_elem in parsed.cssselect(sel):
            tds = tr_elem.cssselect('td')
            if len(tds) != 5:
                continue
            rec = ProxyRecord()
            rec.ip = tds[0].text.strip()
            rec.port = tds[1].text.strip()
            rec.type = 'http'
            yield rec

    def parse_archive_response(self, res, **kwargs):
        super().parse_response(res)
        parsed = HTMLParser.fromstring(res.content)
        sel = 'table > tbody > tr'
        for tr_elem in parsed.cssselect(sel):
            tds = tr_elem.cssselect('td')
            if len(tds) != 6:
                continue
            rec = ProxyRecord()
            rec.ip = tds[0].text.strip()
            rec.port = tds[1].text.strip()
            rec.type = 'http'
            yield rec


if __name__ == '__main__':
    # print(len(list(FeilongProxyDataCollector().get_data())))
    # print(len(list(WuyouProxyDataCollector().get_data())))
    # print(len(list(XiciProxyDataCollector().get_data())))
    # print(len(list(IP181ProxyDataCollector().get_data())))
    print(len(list(CNProxyDataCollector().get_data())))
