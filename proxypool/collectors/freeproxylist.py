import re

from lxml import html as HTMLParser

from ._base import BaseProxyDataCollector, ProxyRecord


class PreeproxylistDataCollector(BaseProxyDataCollector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'http://www.freeproxylists.net/zh/'

    def parse_response(self, res, **kwargs):
        super().parse_response(res)
        parsed = HTMLParser.fromstring(res.content)
        sel = 'table.DataGrid > tr'
        for tr_elem in parsed.cssselect(sel):
            tds = tr_elem.cssselect('td')
            if len(tds) != 10:
                continue
            ip_script = tds[0].cssselect('script')
            if not ip_script:
                continue
            try:
                ip_script = re.search(r'"(.+)"', ip_script[0].text).group(1)
            except (IndexError, ValueError):
                continue
            ip_script = ip_script.encode('utf-8')
            ip_script = ip_script.replace(b'+', b'\x20')
            ip_script = re.sub(
                r'%([a-fA-F0-9][a-fA-F0-9])',
                lambda x: chr(int(x.group(1), 16)).encode('utf-8'),
                ip_script
            )
            ip_script = ip_script.decode('utf-8')
            try:
                ip = re.search(r'>(.+)<', ip_script).group(1)
            except (ValueError, IndexError):
                continue
            rec = ProxyRecord()
            rec.ip = ip
            rec.port = tds[1].text
            rec.type = tds[2].text.lower()
            yield rec


ls = list(PreeproxylistDataCollector().get_data())
print(ls)
