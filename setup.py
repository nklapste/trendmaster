#!/usr/bin/python
# -*- coding: utf-8 -*-

"""setup.py for trendmaster"""

import sys
import os
from setuptools import setup, find_packages
from setuptools.command.test import test


class PyTest(test):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        test.initialize_options(self)
        os.makedirs("test-reports", exist_ok=True)
        self.pytest_args = "-v --cov=trendmaster"

    def run_tests(self):
        import shlex
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


def readme():
    with open("README.rst") as f:
        return f.read()


setup(
    name="trendmaster",
    version="0.0.0",
    description="",
    long_description=readme(),
    author="Nathan Klapstein",
    author_email="nklapste@ualberta.ca",
    url="https://github.com/nklapste/trendmaster",
    download_url="https://github.com/nklapste/trendmaster/",  # TODO
    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    package_data={
        "": ["README.rst"],
    },
    entry_points={
        "console_scripts": [
            "trendmaster = trendmaster.__main__:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=[
        "pytrends>=4.3.0,<5.0.0",
        "discord.py>=0.16.12,<1.0.0",
    ],
    tests_require=[
        "pytest",
        "pytest-cov",
    ],
    cmdclass={'test': PyTest},
)
