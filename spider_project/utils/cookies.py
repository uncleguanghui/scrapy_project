"""
cookies 管理工具
@Time    : 2021/2/8 2:00 下午
@Author  : zhangguanghui
"""
import sys
import json
import signal
import asyncio
import logging
import requests
from time import sleep
from pathlib import Path
from pyppeteer import launch
from spider_project.settings import local_cookies_store
from spider_project.settings_account import USERNAME, PASSWORD

# 在 Linux 下可以简单地将 SIGCHLD 信号的操作设为SIG_IGN，内核在子进程结束时不会产生僵尸进程
if sys.platform == 'linux':
    signal.signal(signal.SIGCLD, signal.SIG_IGN)


# 一些 pyppeteer 操作
# 打开 Chromium 时关闭提示框
# browser = await launch(headless=False, args=['--disable-infobars'])
# 跳转
# await page.goto(url)
# 规避 webdriver 检测
# await page.evaluate('() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }')
# UA伪装
# await self.page.setUserAgent('xxx')
# 等待
# await asyncio.sleep(1)
# 截图
# await page.screenshot({'path':'example1.png'})
# 设置页面视图
# await page.setViewport({'width': 1280, 'height': 1200})
# 打字
# await page.type('selector', 'string', {'delay': 100})
# 点击
# await page.click('selector')
# 关闭浏览器
# await browser.close()
# 获得元素的 style 属性的 visibility 值
# wrong = await page.Jeval('.wrong', 'node => node.style.visibility')
# await page.evaluate('e => e.innerHTML', footer)
# await (await item.getProperty('textContent')).jsonValue()
# 修改元素的值（如清空 input ）
# await page.evaluate('e => { e.value="" }', ele)

def run_async(func, *args, **kwargs):
    """
    运行 async 异步函数
    :param func:
    :return:
    """
    if sys.version_info < (3, 7):
        results = asyncio.get_event_loop().run_until_complete(func(*args, **kwargs))
    else:
        results = asyncio.run(func(*args, **kwargs))
    return results


async def get_xxx_cookies():
    """
    使用 pyppeteer 模拟登录并获得 cookies
    """
    from spider_project import captcha

    # 打开浏览器，进入登录页
    browser = await launch(args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-infobars'], logLevel='ERROR')
    page = await browser.newPage()
    await page.evaluateOnNewDocument('() => {Object.defineProperties(navigator, {webdriver:{get: () => false}})}')
    await page.goto('登录页')
    await page.setViewport({'width': 1280, 'height': 1200})

    # 连续尝试 5 次登录，如果都失败了，则报错
    try_cnt, max_try, login_success = 0, 5, False
    ocr_results = []  # 缓存 OCR 识别错误的情况
    while try_cnt < max_try:
        # 初始化输入框
        username_input, verification_input = await page.xpath('//input[@class="bk2"]')
        password_input = (await page.xpath('//input[@class="bk1"]'))[0]
        await page.evaluate('e => {e.value=""}', username_input)  # 清空已有的输入
        await page.evaluate('e => {e.value=""}', password_input)  # 清空已有的输入
        await page.evaluate('e => {e.value=""}', verification_input)  # 清空已有的输入

        # 输入账号密码
        await username_input.type(USERNAME, {'delay': 100})
        await password_input.type(PASSWORD, {'delay': 100})

        # 输入验证码
        img = (await page.xpath('//img[@id="imageCode"]'))[0]
        img_64 = await img.screenshot(encoding='base64')  # 截图，保存为 base64 编码
        result = captcha.recognize(img_64, img_type='base64', captcha_type=1035)  # 验证码识别，接口类别 1035 代表计算结果验证
        await verification_input.type(result, {'delay': 100})

        # 点击登录
        login_button = (await page.xpath('//button[@class="butt"]'))[0]
        await login_button.click()
        await asyncio.sleep(5)  # 等待 5 秒
        await page.waitForSelector('html')  # 因为会发生页面跳转，page 会失效，所以要加上这么一句

        # 验证是否通过验证码
        wrong_text = await page.xpath('//p[@class="wrong"]')
        if wrong_text:
            # 获得错误信息
            wrong_msg = await page.Jeval('.wrong', 'node => node.innerHTML')
            if wrong_msg == '验证码错误':
                login_success = False
            elif wrong_msg:
                # 非【验证码错误】的错误，都是需要手动解决的错误，因此直接报错，中止脚本
                raise PermissionError(wrong_msg)
        else:
            login_success = True

        if login_success:
            break
        else:
            ocr_results.append([img_64, result])
            try_cnt += 1
            sleep(2)
    if not login_success:
        raise ValueError(f'验证码错误次数超过上限 {max_try} 次')

    # 获取 cookies
    cookies = await page.cookies()
    cookies = {c['name']: c['value'] for c in cookies}

    # 关闭浏览器
    await browser.close()
    await asyncio.sleep(2)

    return cookies


class CookiesBase:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        try:
            self.dir_cookies = Path(__file__).parent.parent / 'cookies'
            self.dir_cookies.mkdir(exist_ok=True)
        except NotADirectoryError:
            self.logger.warning(f'无法创建文件夹 {self.dir_cookies}')
        except Exception as err:
            self.logger.warning(f'创建文件夹 {self.dir_cookies} 时产生了未知错误 {str(err)}')
        self.cookies = None
        self.filename = None  # 文件名
        self.get_func = None  # 模拟登录的异步函数

    def call(self) -> requests.Response:
        """
        需要被重写的调用函数，返回可以用 json 格式解析内容的 response
        :return:
        """
        raise NotImplementedError("必须重新定义 call 函数，用于测试 cookies 是否有效")

    def init(self):
        """
        执行初始化。会依次检查 cookies 是否有效，如果无效，则会重新获取 cookies
        :return:
        """
        assert self.filename is not None, '请先定义 cookie 文件名'
        assert self.get_func is not None, '请先定义模拟登录的异步函数'

        # 看 cookies 文件是否存在，若存在且能 ping 通，则代表 cookies 有效
        if local_cookies_store:
            path_cookies = self.dir_cookies / self.filename
            if path_cookies.exists():
                # 加载 cookies
                with open(path_cookies, 'r') as f:
                    self.cookies = json.load(f)
                # 测试是否能 ping 通
                success, status_code, ping_text, error_info = self.ping()
                if not success:
                    self.logger.warning(f'{self.filename} 测试 URL 失败 {status_code}，错误信息：{error_info}')
                    self.logger.warning(f'{self.filename} 测试结果：\n{ping_text}')
            else:
                self.logger.warning(f'{path_cookies} 文件不存在')
                success = False

            # 如果 cookies 无效，则重新获取
            if not success:
                self.cookies = run_async(self.get_func)

                # 保存 cookies
                try:
                    with open(path_cookies, 'w') as f:
                        json.dump(self.cookies, f)
                except NotADirectoryError:
                    self.logger.warning(f'无法保存 cookies 到 {path_cookies}')
        else:
            self.cookies = run_async(self.get_func)

        self.logger.debug(f'使用 Cookies {json.dumps(self.cookies)}')

    def ping(self) -> (bool, int, str, str):
        """
        测试 cookie 是否有效
        :return:
        """
        assert self.cookies is not None, '请先获取 cookies'

        # 获取测试响应结果
        response = self.call()

        # 可被解析为 json ，且状态码正确
        if len(response.history) > 0:
            for i, history in enumerate(response.history):
                self.logger.warning(f'测试 URL 第 {i} 次重定向：{history.headers["location"]}')
        try:
            result = json.loads(response.text)
            assert isinstance(result, dict), '结果类型错误'
            return 200 <= response.status_code < 300, response.status_code, response.text, ''
        except json.decoder.JSONDecodeError as err:
            return False, response.status_code, response.text, str(err)
        except AssertionError as err:
            return False, response.status_code, response.text, str(err)


class XXXCookies(CookiesBase):
    def __init__(self):
        super().__init__()
        self.filename = 'xxx.json'  # 文件名
        self.get_func = get_xxx_cookies()  # 模拟登录的异步函数

    def call(self):
        """
        中煤的 cookies test url 的 response
        """
        return requests.post(
            url='http://ego.chinacoal.com/pm-common/base/index/header/notification.rpc.do',
            cookies=self.cookies,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, '
                              'like Gecko) Chrome/85.0.4183.102 Safari/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            },
        )


class CookiesManager:
    # cookies 管理器
    def __init__(self):
        self.xc = XXXCookies()

    def init(self):
        """
        初始化，获取最新的 cookies 。
        在脚本中，会在 CookiesMiddleware 初始化的时候后执行
        :return:
        """
        self.xc.init()

    def get_cookies(self, key):
        if key == 'project':
            return self.xc.cookies
        else:
            raise KeyError('暂时还不支持其他类型的 cookies ')
