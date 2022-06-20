import logging
import socket
import urllib2
import ssl
import pyping
import subprocess32

import powergslb.system

__all__ = ['CheckThread']


class CheckThread(powergslb.system.AbstractThread):
    """
    PowerGSLB check thread
    """

    def __init__(self, monitor, content_id, cache, **kwargs):
        super(CheckThread, self).__init__(**kwargs)
        self._fall = 0
        self._rise = 0
        self.monitor = monitor
        self.content_id = content_id
        self.cache = cache
        self.sleep_interval = self.monitor['interval']

    def clean_pdns_cache(self):
        if 'powerdns' in powergslb.system.get_config().items('monitor'):
            url_base = "http://%s/api/v1/servers/localhost/cache/flush?domain=%s."
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            for qname in self.cache.gslb_check_names(self.content_id):
                try:
                    logging.debug('cleaning %s from powerdns by http api' % qname)
                    url = url_base % (powergslb.system.get_config().get('monitor', 'powerdns'), qname)
                    request = urllib2.Request(url)
                    request.add_header('X-API-Key', powergslb.system.get_config().get('monitor', 'pdns-api-key'))
                    request.get_method = lambda: 'PUT'
                    opener.open(request)
                except urllib2.URLError as e:
                    logging.error('error in cleaning %s from powerdns by http api: %s' % (qname, e))

    def _check_fall(self):
        self._fall += 1
        self._rise = 0

        if self._fall >= self.monitor['fall'] and not self.cache.check_status(self.content_id):
            logging.info('{}: {}: status fall'.format(self.name, self.monitor))
            self.clean_pdns_cache()
            self.cache.add_status(self.content_id)

    def _check_rise(self):
        self._fall = 0
        self._rise += 1

        if self._rise >= self.monitor['rise'] and self.cache.check_status(self.content_id):
            logging.info('{}: {}: status rise'.format(self.name, self.monitor))
            self.clean_pdns_cache()
            self.cache.clean_status(self.content_id)

    def _do_exec(self):
        return subprocess32.call(self.monitor['args'], timeout=self.monitor['timeout']) == 0

    def _do_http(self):
        urllib2.urlopen(self.monitor['url'], timeout=self.monitor['timeout'])
        return True

    def _do_icmp(self):
        try:
            ip = self.monitor['ip']
            timeout = self.monitor['timeout'] * 1000
            return pyping.ping(ip, timeout, count=1).ret_code == 0
        except SystemExit:
            raise Exception('unknown host: {}'.format(self.monitor['ip']))

    def _do_tcp(self):
        address = (self.monitor['ip'], self.monitor['port'])
        socket.create_connection(address, self.monitor['timeout']).close()
        return True

    """
    Check http/https get code status (200 - OK, other 40x&50x - error)
    """
    
    def _do_code(self):
        req_url = self.monitor['url']
        req_host = self.monitor['host']
        req_header = {"Host":req_host}
        req_user_agent = {"User-agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5"}
        request = urllib2.Request(req_url,None,req_header,req_user_agent)
        try:
                code = urllib2.urlopen(request,context=ssl._create_unverified_context(),timeout=5)
                answer = code.read()
#                if code.getcode() == 200: logging.info('Host {} via url {} send {} OK, answer:\n{}'.format(req_host,req_url,code.getcode(),answer))
                if code.getcode() == 200: logging.info('Host {} via url {} send {} OK'.format(req_host,req_url,code.getcode()))
                return True
        except urllib2.HTTPError, ercode:
                logging.info('ERROR! Host {} have a error: {}'.format(req_host,ercode))
                return False
        except urllib2.URLError, ercode:
                logging.info('ERROR! Cant connect to host {}, because {}'.format(req_host,ercode))
                return False

    """
    """

    def task(self):
        try:
            if getattr(self, '_do_' + self.monitor['type'])():
                logging.debug('{}: {}: return True'.format(self.name, self.monitor))
                self._check_rise()
            else:
                logging.debug('{}: {}: return False'.format(self.name, self.monitor))
                self._check_fall()
        except Exception as e:
            logging.debug('{}: {}: return Exception: {}: {}'.format(self.name, self.monitor, type(e).__name__, e))
            self._check_fall()
