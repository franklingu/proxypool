from lxml import html as HTMLParser

from ._base import (
    BaseProxyDataCollector, ProxyRecord, _get_requests_session, _send_request
)


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
