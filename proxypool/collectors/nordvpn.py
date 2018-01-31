from ._base import (
    BaseProxyDataCollector, ProxyRecord, _get_requests_session, _send_request
)


class NordvpnDataCollector(BaseProxyDataCollector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = (
            'https://nordvpn.com/free-proxy-list/'
        )
        self.url = ('https://nordvpn.com/wp-admin/admin-ajax.php')

    def get_data(self):
        params = {
            'searchParameters[0][name]': 'proxy-country',
            'searchParameters[0][value]': '',
            'searchParameters[1][name]': 'proxy-ports',
            'searchParameters[1][value]': '',
            'offset': '0',
            'limit': '25',
            'action': 'getProxies',
        }
        with _get_requests_session() as ses:
            res = _send_request(
                ses, self.base_url, self.retry, self.sleep, self.timeout
            )
            res = _send_request(
                ses, self.url, self.retry, self.sleep, self.timeout,
                params=params
            )
            try:
                obj = res.json()
                for raw_rec in obj:
                    rec = ProxyRecord()
                    rec.ip = raw_rec['ip']
                    rec.port = raw_rec['port']
                    rec.type = raw_rec['type'].lower()
                    if 'sock' in rec.type:
                        continue
                    yield rec
            except ValueError:
                pass
