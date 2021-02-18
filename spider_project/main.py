"""
运行脚本，用于 debug
@Time    : 2021/2/8 11:56 上午
@Author  : zhangguanghui
"""
import sys
import os
from scrapy.cmdline import execute

if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    execute(['scrapy', 'crawl', 'project'])
