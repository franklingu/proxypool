import re

from lxml import html as HTMLParser

from ._base import BaseProxyDataCollector, ProxyRecord


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
