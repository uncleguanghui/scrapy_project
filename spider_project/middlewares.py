import random
import logging
import requests
from pathlib import Path
from scrapy.exceptions import IgnoreRequest
from spider_project import email, cm, mysql


class ErrorCodeMiddleware:
    # 处理一些异常状态码
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.errors = []

    def process_spider_input(self, response, spider):
        """
        在 Response 发送给 Spider 之前被调用
        :param response:
        :param spider:
        :return:
        * 当返回是 None 时，Scrapy 将继续处理该 Response ，接着执行更低优先级的中间件的 process_spider_input 方法。
        * 当抛出异常时，Response 的 errback() 方法会被回调，其输出会被重新输入到中间件中，使用 process_spider_output 来处理
        """
        if response.status in spider.settings.get('HTTPERROR_ALLOWED_CODES', []):
            self.logger.warning(str(response.request.meta.get('redirect_urls')))
            raise ValueError(response.text)
        return None

    def process_spider_exception(self, response, exception, spider):
        """
        当 Spider 或其他 Spider 中间件的 process_spider_input() 方法抛出异常时被调用
        :param response:
        :param exception:
        :param spider:
        :return:
        * 当返回是 None 时，Scrapy 将继续处理该 Exception ，接着执行更低优先级的中间件的 process_spider_exception 方法。
        * 当返回 Request 或 Item 的可迭代对象时，所有更低中间件的 process_spider_exception 会被依次执行。
        """
        self.logger.error(f'处理过程中出现异常 {response.status}：{response.text}')
        self.errors.append(response.text)

    def close_spider(self, spider):
        if self.errors:
            subject = f'爬虫过程中有 {len(self.errors)} 条异常记录'
            body = '<p></p>'.join(self.errors)
            email.send_email(subject=subject, body=body)


class IgnoreNoChangesRequestMiddleware:
    # 过滤掉时间没变化的Request
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 获取已经爬过的数据的结束时间
        sql = """
SELECT
    string,
    datetime
FROM
    project
        """
        self.dict_end_time = {data[0]: str(data[1]) for data in mysql.execute(sql)}

    def process_request(self, request, spider):
        """
        过滤掉已经爬过数据、且结束时间没变化的 Request
        :param request:
        :param spider:
        :return:
        """
        meta = request.meta
        history_end_time = self.dict_end_time.get(meta.get('id'))
        if history_end_time:
            new_end_time = meta.get('enroll_end_time')
            if str(new_end_time) == str(history_end_time):
                raise IgnoreRequest(f"丢弃时间没有变化的项目请求 {meta.get('id')}, {history_end_time}")


class HeaderMiddleware:
    # 设置 header
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.headers = {
            # 'Host': '',  # 不要设置!!!
            # 'Content-Length': '',  # 不要设置!!!
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            # 'User-Agent': None,  # 根据实际情况加
            # 'Cookie': None,  # 根据实际情况加
            # 'Origin': None,  # 根据实际情况加
            # 'Referer': None,  # 根据实际情况加
        }

    def process_request(self, request, spider):
        for key, value in self.headers.items():
            request.headers[key] = value
        return None


class RandomUserAgentMiddleware:
    # 随机设置 User-Agent
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        user_agents = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/85.0.4183.102 Safari/537.36"]
        dir_user_agents = Path(__file__).parent / 'user_agents.txt'
        if dir_user_agents.exists():
            user_agents = []
            with open(dir_user_agents, 'r') as f:
                for line in f.readlines():
                    user_agents.append(line.strip())
        self.user_agents = user_agents

    def process_request(self, request, spider):
        request.headers["User-Agent"] = random.choice(self.user_agents)  # 随机选择 user-agent ，便于伪装身份
        return None


class CookiesMiddleware:
    # 设置 cookies
    def __init__(self):
        cm.init()

    def process_request(self, request, spider):
        request.cookies = cm.get_cookies(spider.name)


class ProxyMiddleware:
    # 设置代理
    def __init__(self, proxy_url):
        self.proxy_url = proxy_url

    def get_random_proxy(self):
        try:
            response = requests.get(self.proxy_url)
            if response.status_code == 200:
                proxy = response.text
                return proxy
        except requests.ConnectionError:
            return None

    def process_request(self, request, spider):
        if self.proxy_url:
            proxy = self.get_random_proxy()
            if proxy:
                url = f'https://{proxy}'
                request.meta['proxy'] = url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            proxy_url=crawler.settings.get('PROXY_URL')
        )
