import logging
import argparse
import sys
import traceback

from netaddr import IPNetwork

sys.path.append('/opt')

from powergslb.monitor.cache import Cache
from powergslb.server import CacheResolve

import powergslb.system

__all__ = ['PipeBackend']

class PipeBackend(object):

    @staticmethod
    def main():
        args_parser = argparse.ArgumentParser()
        args_parser.add_argument('-c', '--config')
        args = args_parser.parse_args()

        powergslb.system.parse_config(args.config)
        config = powergslb.system.get_config()

        logging.basicConfig(
                format=config.get('logging', 'format'),
                level=logging.getLevelName(config.get('logging', 'level'))
        )

        try:
            proto = sys.stdin.readline()
            if proto != "HELO\t5\n":
                print("FAIL")
                sys.stdin.readline()
                exit()
            else:
                print("OK       Sample backend firing up")

            with Cache(**powergslb.system.get_config().items('cache')) as cache:
                resolver = CacheResolve(cache)
                logging.debug('cache initiated')

                while True:
                    line = sys.stdin.readline().strip()
                    logging.debug("Received: "+line)
                    req = line.split("\t")

                    if req[0] == "CMD":
                        print(req[1]+"\nEND")
                    elif len(req) < 8:
                        print("LOG       PowerDNS sent unparseable line\nFAIL")
                    else:
                        qname = req[1]
                        qclass = req[2]
                        qtype = req[3]
			ip = IPNetwork(req[7]).ip
			
                        res = resolver.resolve(qname.lower(), qtype, ip)
                        for r in res:
                            p = ["DATA", '0', '1', r['qname'], qclass, r['qtype'], r['ttl'], '-1', r['content']]
                            if r['qtype'] in ['MX', 'SRV']: p.insert(-1, r['priority'])
                            print("\t".join(map(str, p)))
                        print("END")
        except Cache.Error as e:
            pass
            logging.error('{}: {}: {}'.format(type(self).__name__, type(e).__name__, e))


if __name__ == "__main__":
  try:
    PipeBackend.main()
  except Exception as e:
    print(e)
    traceback.print_exc()
