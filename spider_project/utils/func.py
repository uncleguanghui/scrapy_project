"""
工具函数类
@Time    : 2021/2/7 7:15 下午
@Author  : zhangguanghui
"""


def make_item(res: dict, cls):
    """
    构造 Item 实例，并尽可能尝试从 response 里自动读取到目标值，如果读取不到，还需要在外部赋值。
    :param res:
    :param cls:
    :return:
    """
    item = cls()
    for field in cls.field_names():
        item[field] = res.get(field)
    return item
