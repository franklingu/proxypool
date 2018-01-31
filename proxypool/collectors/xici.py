from datetime import datetime, timedelta

from lxml import html as HTMLParser

from ._base import (
    BaseProxyDataCollector, ProxyRecord, _get_requests_session, _send_request
)


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
