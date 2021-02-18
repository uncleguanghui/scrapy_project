"""
MySQL 数据库管理器
@Time    : 2021/2/9 10:45 上午
@Author  : zhangguanghui
"""
import logging
import warnings
from sqlalchemy import create_engine
from pathlib import Path
from spider_project.settings_account import MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_HOST, MYSQL_PORT, MYSQL_USER

warnings.filterwarnings("ignore")


class MySQL:
    def __init__(self):
        self.engine = create_engine(
            f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/'
            f'{MYSQL_DATABASE}?charset=utf8mb4',
        )
        self.logger = logging.getLogger(__name__)

    def execute(self, sql, *args, **kwargs):
        """
        只读操作，不提交
        :param sql:
        :param args:
        :param kwargs:
        :return:
        """
        with self.engine.connect().execution_options(autocommit=False) as connection:
            return connection.execute(sql, *args, **kwargs).fetchall()

    def execute_commit(self, sql, *args, **kwargs):
        """
        开启事务，提交
        :param sql:
        :param args:
        :param kwargs:
        :return:
        """
        with self.engine.begin() as connection:
            connection.execute(sql, *args, **kwargs)

    def create_tables(self):
        """
        建表
        :return:
        """
        # 建表
        dir_sql = Path(__file__).parent.parent / 'sql'
        if dir_sql.exists():
            for file in dir_sql.iterdir():
                if file.suffix == '.sql':
                    with open(file, 'r') as f:
                        sql = '\n'.join(f.readlines())
                        self.execute_commit(sql)

        # 插入默认数据
        companies = """
        a,2020-01-01 00:00:00,2
        """
        for line in companies.split('\n'):
            if line.strip():
                string, datetime, integer = [i.strip() for i in line.strip().split(',')]
                self.execute_commit('REPLACE INTO company(`string`, `datetime`, `integer`) VALUES (%s, %s, %s)',
                                    (string, datetime, integer))
