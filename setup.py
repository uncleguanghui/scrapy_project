# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages
from distutils.command.clean import clean
import subprocess
import os
import shutil


class CleanHook(clean):
    def run(self):
        clean.run(self)

        def maybe_rm(path):
            if os.path.exists(path):
                shutil.rmtree(path)

        maybe_rm('project.egg-info')
        maybe_rm('.pytest_cache')
        maybe_rm('build')
        maybe_rm('dist')
        maybe_rm('.eggs')
        maybe_rm('htmlcov')
        subprocess.call('rm -rf .coverage', shell=True)
        subprocess.call('rm -rf *.egg', shell=True)
        subprocess.call('rm -f datastore.db', shell=True)
        subprocess.call(r'find . -name "*.pyc" -exec rm -rf {} \;',
                        shell=True)


setup(
    name='project',
    version='1.0',
    packages=find_packages(),
    entry_points={'scrapy': ['settings = spider_project.settings']},
    include_package_data=True,
    package_data={'key': ['sql/*.sql', 'user_agents.txt']},
    cmdclass={
        'clean': CleanHook,  # python setup.py clean 清理工作区
    },
)
