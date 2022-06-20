import json

from powergslb.server.http.handler.abstract import AbstractContentHandler
from powergslb.server.resolve import CacheResolve

__all__ = ['PowerDNSContentHandler']


class PowerDNSContentHandler(AbstractContentHandler):
    """
    PowerDNS content handler
    """

    def _get_lookup(self):
        resolver = CacheResolve(self.cache)
        return resolver.resolve(self.dirs[2], self.dirs[3], self.remote_ip)

    def content(self):
        if len(self.dirs) == 4 and self.dirs[1] == 'lookup':
            content = {'result': self._get_lookup()}
        else:
            content = {'result': False}

        return json.dumps(content, separators=(',', ':'))
