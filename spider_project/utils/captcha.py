"""
验证码处理类
使用冰拓的验证码识别 API
@Time    : 2021/2/9 10:50 上午
@Author  : zhangguanghui
"""
import json
import base64
import logging
import requests
from pathlib import Path
from spider_project.settings_account import API_PASSWORD, API_USERNAME


class Captcha:
    def __init__(self):
        self.api_url = "http://www.bingtop.com/ocr/upload/"
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def params(img64: bytes, captcha_type: int) -> dict:
        """
        请求参数
        :param img64: base64 编码的 bytes 格式的图像数据
        :param captcha_type: 验证码编号 http://www.bingtop.com/type/
        :return:
        """
        return {
            "username": API_USERNAME,
            "password": API_PASSWORD,
            "captchaData": img64,
            "captchaType": captcha_type  # 接口类别
        }

    def recognize(self, img: (Path, str, bytes), img_type='file', captcha_type=1001) -> str:
        """
        调用冰拓的 api 接口来解析验证码。

        python api 文档地址：http://www.bingtop.com/static/html/python.html
        captchaType 文档地址：http://www.bingtop.com/type/

        :param img: 可以传入图片的路径，也可以直接传入 base64 编码的图片
        :param img_type: file 或者 base64
        :param captcha_type: 验证码识别类型
        :return:
        """
        assert img_type in ('file', 'base64')

        # 获得 base64 编码的图片
        if img_type == 'file':
            assert isinstance(img, (str, Path))
            with open(img, 'rb') as pic_file:
                img64 = base64.b64encode(pic_file.read())
        else:
            if not isinstance(img, bytes):
                img64 = bytes(str(img), encoding='utf8')  # 转换为 bytes
            else:
                img64 = img

        # 调用接口
        response = requests.post(self.api_url, data=self.params(img64=img64, captcha_type=captcha_type))
        data = json.loads(response.text)

        if data.get('code') != 0:
            self.logger.warning('验证码解析失败：', data.get('message'))
            return ''
        return data.get('data', {}).get('recognition')
