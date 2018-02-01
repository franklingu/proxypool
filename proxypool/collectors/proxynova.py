import re

from lxml import html as HTMLParser

from ._base import BaseProxyDataCollector, ProxyRecord


class ProxynovaDataCollector(BaseProxyDataCollector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = (
            'https://www.proxynova.com/proxy-server-list/anonymous-proxies'
        )

    def parse_response(self, res, **kwargs):
        super().parse_response(res)
        parsed = HTMLParser.fromstring(res.content)
        sel = 'table#tbl_proxy_list > tbody > tr'
        for tr_elem in parsed.cssselect(sel):
            tds = tr_elem.cssselect('td')
            if len(tds) != 8:
                continue
            patt = r"('[\d\.]+'|\(\d+\))"
            ip = tds[0].cssselect('abbr > script')[0].text.strip()
            match = re.findall(patt, ip)
            if len(match) != 3:
                continue
            try:
                ip = match[0].strip("'")[int(match[1].strip('(').strip(')')):]
                ip += match[2].strip("'")
            except (ValueError, IndexError):
                continue
            port = (''.join(tds[1].itertext())).strip()
            rec = ProxyRecord()
            rec.ip = ip
            rec.port = port
            rec.type = 'http'
            yield rec
