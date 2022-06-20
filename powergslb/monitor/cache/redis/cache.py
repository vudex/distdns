import logging

import redis
import hashlib
import json

import powergslb.database
import powergslb.system

__all__ = ['RedisCache']

class RedisCache(redis.Redis):
    Error = redis.RedisError
    _status_key = "contents:check"
    _base_key = "record"

    def __enter__(self):
        return self

    def __exit__(self, *_):
      pass

    def __init__(self, **kwargs):
      if 'update_interval' in kwargs: kwargs.pop('update_interval')
      super(RedisCache, self).__init__(**kwargs)

    def reload(self):
      records_hash_key = "records:check"

      with powergslb.database.Database(**powergslb.system.get_config().items('database')) as db:
        rows = db.gslb_records()

      rows_hash = hashlib.sha1(json.dumps(rows, sort_keys=True)).hexdigest()
      cache_hash = self.get(records_hash_key)

      if rows_hash != cache_hash:
        logging.info('{}: update cache from the database'.format(type(self).__name__))
        pipe = self.pipeline()

        for key in self.scan_iter(self._status_key + ":*"):
          pipe.delete(key)
        for key in self.scan_iter(self._base_key + ":*"):
          pipe.delete(key)
        pipe.delete(self._base_key)

        for row in rows:
          #pipe.sadd(self._base_key, row['qname'])

          name_key = self._base_key + ":" + row['qname']
          pipe.sadd(name_key, row['qtype'])

          name_type_key = name_key + ":" + row['qtype']
          pipe.sadd(name_type_key, row['recid'])

          row_key = name_type_key + ":" + str(row['recid'])
          pipe.hmset(row_key, row)

          monitor_key = self._status_key + ":" + str(row['id'])
          pipe.sadd(monitor_key, row['qname'])

        self.set(records_hash_key, rows_hash)
        pipe.execute()
      else:
        logging.info('{}: no rows update needed'.format(type(self).__name__))

    def gslb_check_names(self, content_monitor_id):
      monitor_key = self._status_key + ":" + str(content_monitor_id)
      return self.smembers(monitor_key)

    def gslb_records(self, qname, qtype):
      logging.debug('Redis request: [%s, %s]' % (qname, qtype))
      rows = []
      name_key = self._base_key + ":" + qname

      for row_type in self.smembers(name_key):
        if (qtype == row_type or qtype == "ANY"):
          name_type_key = name_key + ":" + row_type

          for recid in self.smembers(name_type_key):
            row_key = name_type_key + ":" + recid
            rows.append(self.hgetall(row_key))

      return rows

    def get_status(self):
      return self.smembers(self._status_key)

    def check_status(self, member):
      return self.sismember(self._status_key, member)

    def clean_status(self, *members):
      pipe = self.pipeline()
      for member in members:
        self.srem(self._status_key, member)
      pipe.execute()

    def add_status(self, *members):
      pipe = self.pipeline()
      for member in members:
        self.sadd(self._status_key, member)
      pipe.execute()
