from lxml import html as HTMLParser

from ._base import (
    BaseProxyDataCollector, ProxyRecord, _get_requests_session, _send_request
)


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
