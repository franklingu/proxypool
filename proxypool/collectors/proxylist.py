import re
import base64
import urllib

from lxml import html as HTMLParser

from ._base import (
    BaseProxyDataCollector, ProxyRecord, _get_requests_session, _send_request
)


class ProxyListProxyDataCollector(BaseProxyDataCollector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'https://proxy-list.org/english/index.php'

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
                    '#proxy-table > div.table-wrap > div > ul'
                )
                for ul_elem in parsed.cssselect(sel):
                    rec = ProxyRecord()
                    ip_port = ul_elem.cssselect('li.proxy script')[0].text
                    patt = "'(.+)'"
                    match = re.search(patt, ip_port)
                    if not match:
                        continue
                    ip_port = base64.b64decode(match.group(1)).decode('utf-8')
                    patt = r'(\d+\.\d+\.\d+\.\d+):(\d+)'
                    match = re.match(patt, ip_port)
                    if not match:
                        continue
                    rec.ip = match.group(1)
                    rec.port = match.group(2)
                    rec.type = (''.join(ul_elem.cssselect(
                        'li.https'
                    )[0].itertext())).strip().lower()
                    yield rec
                if url is None:
                    break
                try:
                    url = urllib.parse.urljoin(
                        self.url,
                        parsed.cssselect('a.next')[0].get('href')
                    )
                except IndexError:
                    url = None
