from dataclasses import dataclass, field, fields


class Base:
    """
    item 的基类。
    这里不使用 scrapy.item 是因为不太方便自定义一些类方法，同时也无法赋予 field 默认值。
    参考的是官方实践：https://docs.scrapy.org/en/latest/topics/items.html#item-objects
    """
    collection = table = None
    key = None

    def __getitem__(self, key):
        # 能够以 data[key] 的方式来获得属性值
        return self.__getattribute__(key)

    def __setitem__(self, key, value):
        # 能够以 data[key] 的方式来设置属性值
        self.__setattr__(key, value)

    @classmethod
    def field_names(cls):
        """
        获取所有 fields 的名称列表
        :return:
        """
        return list(cls().to_dict().keys())

    def fields(self):
        """
        获取所有 fields 列表
        :return:
        """
        return fields(self)

    def to_dict(self):
        """
        生成字典
        :return:
        """
        return self.__dict__

    @classmethod
    def get_default(cls, key):
        """
        获取默认值
        :param key:
        :return:
        """
        return cls()[key]


@dataclass
class ProjectItem(Base):
    collection = table = 'project'  # 表名
    key = 'string'  # unique key

    string: str = field(default='', metadata={'max_length': 64})  # 字符串，默认为空字符串，最大长度为 64
    datetime: str = field(default=None)  # 时间，默认为 None
    integer: int = field(default=0)  # 数量，默认为 0
