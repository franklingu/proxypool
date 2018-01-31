from lxml import html as HTMLParser

from ._base import (
    BaseProxyDataCollector, ProxyRecord, _get_requests_session, _send_request
)


class MimvpProxyDataCollector(BaseProxyDataCollector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.urls = [
            'https://proxy.mimvp.com/free.php?proxy=in_tp',
            'https://proxy.mimvp.com/free.php?proxy=in_hp',
            'https://proxy.mimvp.com/free.php?proxy=out_tp',
            'https://proxy.mimvp.com/free.php?proxy=out_hp',
        ]

    def get_data(self):
        raise NotImplementedError('Requires decode for all images')
        with _get_requests_session() as ses:
            for url in self.urls:
                res = None
                res = _send_request(
                    ses, url, self.retry, self.sleep, self.timeout
                )
                if res is None:
                    continue
                parsed = HTMLParser.fromstring(res.content)
                sel = 'table > tbody > tr'
                for ul_elem in parsed.cssselect(sel):
                    tds = ul_elem.cssselect('td')
                    if len(tds) != 9:
                        continue
                    rec = ProxyRecord()
                    rec.ip = tds[1].text.strip()
                    rec.port = tds[2].text.strip()
                    rec.type = (''.join(tds[3].itertext())).strip().lower()
                    yield rec
