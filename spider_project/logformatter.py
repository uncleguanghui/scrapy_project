from scrapy import logformatter
import logging


class PoliteLogFormatter(logformatter.LogFormatter):
    # 忽略 DropItem 时的警告
    def dropped(self, item, exception, response, spider):
        return {
            'level': logging.DEBUG,
            'msg': logformatter.DROPPEDMSG,
            'args': {
                'exception': exception,
                'item': item,
            }
        }
