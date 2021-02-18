from spider_project.utils.email import Email
from spider_project.utils.mysql import MySQL
from spider_project.utils.captcha import Captcha
from spider_project.utils.api import APIManager
from spider_project.utils.cookies import CookiesManager
from spider_project.utils.files import FileManager
from spider_project.utils.func import *

email = Email()  # 邮箱管理器
mysql = MySQL()  # 数据库管理器
captcha = Captcha()  # 验证码管理器
am = APIManager()  # API 管理器
cm = CookiesManager()  # cookies 管理器
fm = FileManager()  # 文件管理器
