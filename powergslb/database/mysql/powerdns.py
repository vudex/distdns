import abc

__all__ = ['PowerDNSDatabaseMixIn']


class PowerDNSDatabaseMixIn(object):
    """
    PowerDNSDatabaseMixIn class contains PowerDNS related queries
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def _execute(self, operation, params):
        pass

    def gslb_checks(self):
        operation = """
            SELECT `contents_monitors`.`id`,
              `contents`.`content`,
              `monitors`.`monitor_json`
            FROM `contents_monitors`
              JOIN `contents` ON `contents_monitors`.`content_id` = `contents`.`id`
              JOIN `monitors` ON `contents_monitors`.`monitor_id` = `monitors`.`id`
        """

        return self._execute(operation)

    def gslb_check_names(self, content_monitor_id):
        operation = """
          select `names`.`name` AS `qname`
            from `contents_monitors`
                 join `records` on `records`.`content_monitor_id` = `contents_monitors`.`id`
                 join `names_types` on `names_types`.`id` = `records`.`name_type_id`
                 join `names` on `names`.`id` = `names_types`.`name_id`
           where `contents_monitors`.`id` = %s
        """

        return self._execute(operation, (content_monitor_id,))

    def gslb_records(self, qname = None, qtype = None):
        operation = """
            SELECT `names`.`name` AS `qname`,
              `types`.`type` AS `qtype`,
              `names_types`.`ttl`,
              `names_types`.`persistence`,
              `records`.`fallback`,
              `records`.`weight`,
              `contents_monitors`.`id`,
              `contents`.`content`,
              `views`.`rule`,
              `records`.`id` AS `recid`
            FROM `names`
              JOIN `names_types` ON `names`.`id` = `names_types`.`name_id`
              JOIN `types` ON `names_types`.`type_value` = `types`.`value`
              JOIN `records` ON `names_types`.`id` = `records`.`name_type_id`
              JOIN `contents_monitors` ON `records`.`content_monitor_id` = `contents_monitors`.`id`
              JOIN `contents` ON `contents_monitors`.`content_id` = `contents`.`id`
              JOIN `views` ON `records`.`view_id` = `views`.`id`
            WHERE `records`.`disabled` = 0
        """

        params = []

        if qname:
            operation += """
                  AND `names`.`name` = %s
            """
            params.append(qname)

        if qtype and qtype != 'ANY':
            operation += """
                  AND `types`.`type` = %s
            """
            params.append(qtype)

        return self._execute(operation, params)
