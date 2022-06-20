import logging

from powergslb.monitor.cache import Cache
import powergslb.system

__all__ = ['CacheThread']

class CacheThread(powergslb.system.AbstractThread):
    """
    Cache update thread
    """

    def __init__(self, **kwargs):
        super(CacheThread, self).__init__(**kwargs)
        self.config = powergslb.system.get_config().items('cache')
        self.sleep_interval = self.config['update_interval']

    def task(self):
        try:
          cache = Cache(**self.config)
          cache.reload()
        except Cache.Error as e:
          logging.error('{}: {}: {}'.format(type(self).__name__, type(e).__name__, e)) 
