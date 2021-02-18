"""
文件管理类
@Time    : 2021/2/9 10:32 上午
@Author  : zhangguanghui
"""
import sys
import requests
import logging
from pathlib import Path


class FileManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.files = {}  # 缓存文件到内存，为了应对无法保存的情况
        self.current_files_size_mb = 0  # 已缓存的文件大小
        self.max_file_size_mb = 20  # 要缓存的单个文件大小上限
        self.max_files_size_mb = 100  # 要缓存的文件总大小上限

        # 存储附件的路径
        self.dir_files = Path(__file__).parent.parent / 'files'
        try:
            self.dir_files.mkdir(exist_ok=True)
        except NotADirectoryError:
            self.logger.warning(f'无法创建文件夹 {self.dir_files}')
        except Exception as err:
            self.logger.warning(f'创建文件夹 {self.dir_files} 时产生了未知错误 {str(err)}')

    def download(self, url: str, filename: str, *args, **kwargs):
        """
        下载文件
        :param url: 下载路径
        :param filename: 存储文件名，统一存储在 attachments 目录下，如果已存在则覆盖
        :return:
        """
        r = requests.get(url, *args, **kwargs)

        # 基于该文件大小、目前已经缓存的文件大小，判断是否要缓存该文件到内存中
        size_mb = sys.getsizeof(r.content) / 1024 / 1024  # 文件大小，单位为 MB
        if size_mb < self.max_file_size_mb:
            if size_mb + self.current_files_size_mb < self.max_files_size_mb:
                self.files[filename] = r.content
                self.current_files_size_mb += size_mb
            else:
                self.files[filename] = b''
                self.logger.warning(f'已缓存 {len(self.files)} 个文件，总量为 {self.current_files_size_mb:.1f} MB，'
                                    f'目标文件 {filename} 大小为 {size_mb:.1f} MB，'
                                    f'加入后将超过上限 {self.max_files_size_mb:.1f} MB，将以空文件缓存')
        else:
            self.files[filename] = b''
            self.logger.warning(f'目标文件 {filename} 大小为 ({size_mb:.1f} MB，'
                                f'超过上限 {self.max_file_size_mb:.1f} MB，'
                                f'将以空文件缓存')

        # 缓存到本地
        path_file = self.dir_files / filename
        try:
            with open(path_file, "wb") as f:
                f.write(r.content)
            if path_file.exists():
                self.logger.warning(f'成功覆盖文件 {path_file}')
            else:
                self.logger.info(f'写入文件到 {path_file}')
        except NotADirectoryError:
            self.logger.warning(f'无法保存文件到 {path_file}')

    def get_file(self, filename) -> bytes:
        """
        获取文件内容，首先从字典里找，没有的话再搜索本地文件夹
        :param filename:
        :return:
        """
        return self.files.get(filename)
