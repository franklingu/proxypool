from lxml import html as HTMLParser

from ._base import BaseProxyDataCollector, ProxyRecord


class F31DataCollector(BaseProxyDataCollector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'https://31f.cn/'

    def parse_response(self, res, **kwargs):
        super().parse_response(res)
        parsed = HTMLParser.fromstring(res.content)
        sel = 'table > tr'
        for tr_elem in parsed.cssselect(sel):
            tds = tr_elem.cssselect('td')
            if len(tds) != 8:
                continue
            ip = tds[1].text.strip()
            port = tds[2].text.strip()
            if 'socks' in ''.join(tds[4].itertext()):
                continue
            rec = ProxyRecord()
            rec.ip = ip
            rec.port = port
            rec.type = 'http'
            yield rec
