"""
邮箱管理器
@Time    : 2021/2/9 10:46 上午
@Author  : zhangguanghui
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from spider_project.settings_account import MAIL_TO, MAIL_PASS, MAIL_HOST, MAIL_PORT, MAIL_USER


class Email:
    def __init__(self):
        self.mail_host = MAIL_HOST  # 发送邮件的服务器
        self.mail_user = MAIL_USER  # 用户名
        self.mail_pass = MAIL_PASS  # 发送邮箱的授权码
        self.mail_port = MAIL_PORT  # 端口号
        self.mail_to = MAIL_TO  # 收件人列表
        self.logger = logging.getLogger(__name__)

    def send_email(self, subject, body, to=None):
        """
        发送邮件
        :param subject: 主题（邮件 title）
        :param body: 正文
        :param to: 收件人
        :return:
        """
        from spider_project import fm

        message = MIMEMultipart()
        message['From'] = self.mail_user  # 发件人
        message['To'] = to or self.mail_to  # 收件人，如果有多个邮件地址，用","分隔即可。（注意一定要发给自己，不然可能会被判定为垃圾邮件）
        message['Subject'] = subject  # 主题
        message.attach(MIMEText(body, 'html', 'utf-8'))  # 正文

        # 添加附件
        for filename, content in fm.files.items():
            # 不管什么类型的附件，都用MIMEApplication，MIMEApplication默认子类型是application/octet-stream。
            # 表明这是个二进制的文件，然后客户端收到这个声明后，会根据文件扩展名来猜测。
            attachment = MIMEApplication(content)  # content 为读到的 bytes 格式
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            message.attach(attachment)

        server = smtplib.SMTP(self.mail_host, self.mail_port)
        server.starttls()
        # server.set_debuglevel(1)  # 打印邮箱交互详情
        server.login(self.mail_user, self.mail_pass)
        server.sendmail(message['From'], message['To'].split(','), message.as_string())
        server.quit()
