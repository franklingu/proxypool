from datetime import datetime, timedelta

from lxml import html as HTMLParser

from ._base import (
    BaseProxyDataCollector, ProxyRecord, _get_requests_session, _send_request
)


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
