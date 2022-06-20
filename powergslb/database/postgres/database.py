import logging
import time
import psycopg2
import psycopg2.extensions

from powergslb.database.postgres.powerdns import PowerDNSDatabaseMixIn
from powergslb.database.postgres.w2ui import W2UIDatabaseMixIn

__all__ = ['PostgreDatabase']


class PostgreDatabase(PowerDNSDatabaseMixIn, W2UIDatabaseMixIn):
    """
    PostgreDatabase class
    """
    Error = psycopg2.Error

    def __init__(self, **kwargs):
      self.dsn = "dbname=%s host=%s user=%s password=%s sslmode=%s sslrootcert=%s sslcert=%s sslkey=%s" % (kwargs['database'], kwargs['host'], kwargs['user'], kwargs['password'], kwargs['sslmode'], kwargs['sslrootcert'], kwargs['sslcert'], kwargs['sslkey'])
      if 'port' in kwargs: self.dsn += ' port=%d' % (kwargs['port'])
      self.conn = psycopg2.connect(self.dsn)
      if kwargs['autocommit']:
          self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
      while (self.conn.status != 1):
          logging.debug('DB status not ready: {}'.format(self.conn.status))
      logging.debug('DB is ready')


    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.conn.close()

    @staticmethod
    def join_operation(operation):
        return ' '.join(filter(bool, (line.strip() for line in operation.splitlines())))

    def _execute(self, operation, params=()):
        operation = self.join_operation(operation)
        if params:
            logging.debug(str(params))
            logging.debug('{}: "{}" % {}'.format(type(self).__name__, operation, params))
        else:
            logging.debug('{}: "{}"'.format(type(self).__name__, operation))

        cursor = self.conn.cursor()
        try:
            cursor.execute(operation, params)
            if operation.startswith('SELECT'):
                logging.debug('{}: {} rows returned'.format(type(self).__name__, cursor.rowcount))
                column_names = [description[0] for description in cursor.description]
                result = [dict(zip(column_names, row)) for row in cursor]
            else:
                logging.debug('{}: {} rows affected'.format(type(self).__name__, cursor.rowcount))
                result = cursor.rowcount
        finally:
            cursor.close()

        return result
