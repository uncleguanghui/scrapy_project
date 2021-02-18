import logging
import warnings
from datetime import datetime
from collections import deque
from spider_project import email, mysql, fm
from scrapy.exceptions import DropItem

warnings.filterwarnings('ignore')


class DuplicatesPipeline(object):
    # 按照 id 去重
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['string'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['string'])
            return item


class CleanPipeline:
    # 数据清洗
    def process_item(self, item, spider):
        """
        清洗数据，如时间格式转换、字符串最大长度截断
        :param item:
        :param spider:
        :return:
        """
        for field in item.fields():
            # 如果被赋予了 None 值，则恢复为默认值
            if item[field.name] is None:
                item[field.name] = item.get_default(field.name)
            # 如果是时间列，则解析并转化为统一的字符串
            if field in {'datetime'}:
                item[field.name] = datetime.strptime(item[field.name], '%Y-%m-%dT%H:%M:%S.%fZ').replace(
                    microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
            # 字符数据最大长度截断
            if field.type.__name__ == 'str' and 'max_length' in field.metadata:
                item[field.name] = item[field.name][:field.metadata.get('max_length', 0)]

        return item


class MysqlPipeline:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # 存储数据
    def process_item(self, item, spider):
        key = item[item.key]
        assert key

        # 存储到数据库
        # insert，当记录不存在时 insert，当记录存在时 update
        data = item.to_dict()
        insert_keys = ','.join([f'`{key}`' for key in data.keys()])
        insert_values = ','.join(['%s'] * len(data))  # 占位符
        update_sql = ','.join([f'`{key}`=%s' for key in data.keys() if key != item.key])
        sql = f'INSERT INTO {item.table} ({insert_keys}) VALUES ({insert_values}) ON DUPLICATE KEY UPDATE {update_sql}'
        mysql.execute_commit(sql, tuple(data.values()) + tuple(value for key, value in data.items() if key != item.key))

        return item

    def open_spider(self, spider):
        # 建表
        mysql.create_tables()


class MailPipeline:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.items = deque([])

    def process_item(self, item, spider):
        """
        保存 Item
        :param item:
        :param spider:
        :return:
        """
        if item:
            self.items.append(item)

        return item

    def items_format(self, spider):

        # 设置主题
        subject = f'爬虫：新增 {len(self.items)} 个项目'

        # 设置正文，以表格形式呈现 item 的信息
        body = ''
        if self.items:
            body = '<table border="1">'
            body += '<tr><th>字符串</th><th>时间</th><th>数量</th></tr>'
            for item in self.items:
                integer = str(int(float(item["integer"]))) if item["integer"] else ''
                body += (f'<tr><td>{item["string"] or ""}</td>'
                         f'<td>{item["datetime"] or ""}</td>'
                         f'<td>{integer}</td></tr>')
            body += '</table>'

        # 最后，将附件名称添加到正文中
        filenames = ','.join(fm.files.keys())
        body += filenames

        return subject, body

    def close_spider(self, spider):
        """
        Spider 关闭时发送邮件
        :param spider:
        :return:
        """
        subject, body = self.items_format(spider)
        email.send_email(subject=subject, body=body)
