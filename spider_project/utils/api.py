"""
API 接口管理器
@Time    : 2021/2/7 7:43 下午
@Author  : zhangguanghui
"""
import random
import scrapy
import urllib.parse
from datetime import datetime


class API:
    # API 类一个案例，建议按需定制多个 API
    @staticmethod
    def make_get_xxx_params(keyword) -> str:
        """
        创建参数（适用于 get 请求）
        :param keyword:
        :return:
        """
        return urllib.parse.urlencode({'keyword': keyword})

    @staticmethod
    def make_post_xxx_params(keyword: str, start: int, limit: int = 20) -> dict:
        """
        创建参数（适用于 post 请求）
        :param keyword:
        :param start:
        :param limit:
        :return:
        """
        data = {
            'keyword': keyword,
            'start': start,
            'time_stamp': int(datetime.now().timestamp()) * 1000 + random.randint(0, 1000)
        }
        # 修改值格式
        for k, v in data.items():
            data[k] = str(v)
        return data

    def get_xxx(self, keyword, **kwargs):
        """
        获取请求
        :param keyword:
        :return:
        """
        url = 'http://api?' + self.make_get_xxx_params(keyword=keyword)
        return scrapy.Request(url=url, **kwargs)

    def post_xxx(self, keyword: str, start: int, **kwargs):
        """
        获取翻页结果
        :param keyword: 关键字
        :param start: 开始的索引（注意是偏移量，而不是页数）
        :return:
        """
        url = 'http://api'
        form_data = self.make_post_xxx_params(keyword, start)
        return scrapy.FormRequest(url=url, formdata=form_data, **kwargs)


class APIManager:
    # API 管理器
    def __init__(self):
        self.api = API()

    def get_api(self, key):
        """
        获得指定的 api 接口。因为过程中可能会调用不同的 API
        :param key:
        :return:
        """
        if key == 'project':
            return self.api
        else:
            raise KeyError('暂时还不支持其他类型的 API ')
