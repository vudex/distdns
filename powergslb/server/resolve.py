import logging
import netaddr

__all__ = ['CacheResolve']

class CacheResolve(object):

    def __init__(self, cache):
        self.cache = cache

    def _filter_records(self, qtype_records, ip):
        records = []
        for qtype in qtype_records:

            fallback_records = {}
            live_records = {}

            for record in qtype_records[qtype]:
                if not self._is_in_view(record, ip):
                    continue

                if record['fallback']:
                    if record['weight'] not in fallback_records:
                        fallback_records[record['weight']] = []

                    fallback_records[record['weight']].append(record)

                if not self.cache.check_status(record['id']):
                    if record['weight'] not in live_records:
                        live_records[record['weight']] = []

                    live_records[record['weight']].append(record)

            if live_records:
                filtered_records = live_records[max(live_records)]
            elif fallback_records:
                filtered_records = fallback_records[max(fallback_records)]
            else:
                filtered_records = []

            if not filtered_records:
                continue

            if int(filtered_records[0]['persistence']):
                records.append(self._remote_ip_persistence(filtered_records, ip))
            else:
                records.extend(filtered_records)

        return records

    def resolve(self, qname, qtype, ip):
        records = self.cache.gslb_records(qname, qtype)
        qtype_records = self._split_records(records)
        filtered_records = self._filter_records(qtype_records, ip)
        return self._strip_records(filtered_records)

    def _is_in_view(self, record, ip):
        result = False
        try:
            result = bool(netaddr.smallest_matching_cidr(ip, record.get('rule').split()))
        except (AttributeError, netaddr.AddrFormatError, ValueError) as e:
            logging.error('{}: record id {} view rule invalid: {}: {}'.format(type(self).__name__, record['id'], type(e).__name__, e))

        return result

    def _remote_ip_persistence(self, records, ip):
        persistence_value = netaddr.IPAddress(ip).value >> int(records[0]['persistence'])
        return records[hash(persistence_value) % len(records)]

    def _split_records(self, records):
        qtype_records = {}
        for record in records:
            if record['qtype'] in ['MX', 'SRV']:
                content_split = record['content'].split()
                try:
                    record['priority'] = int(content_split[0])
                    record['content'] = ' '.join(content_split[1:])
                except (KeyError, ValueError) as e:
                    logging.error('{}: record id {} priority missing or invalid: {}: {}'.format(type(self).__name__, record['id'], type(e).__name__, e))
                    continue

            if record['qtype'] not in qtype_records:
                qtype_records[record['qtype']] = []

            qtype_records[record['qtype']].append(record)

        return qtype_records

    @staticmethod
    def _strip_records(records):
        result = []
        for record in records:
            if record['qtype'] in ['MX', 'SRV']:
                names = ['qname', 'qtype', 'content', 'ttl', 'priority']
                values = [record['qname'], record['qtype'], record['content'], record['ttl'], record['priority']]
            else:
                names = ['qname', 'qtype', 'content', 'ttl']
                values = [record['qname'], record['qtype'], record['content'], record['ttl']]

            result.append(dict(zip(names, values)))

        return result
