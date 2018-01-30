#!/usr/bin/env python
from __future__ import absolute_import, print_function

from setuptools import setup, find_packages

import data_utils

NAME = 'data_utils'
PACKAGES = find_packages(
    exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']
)
PACKAGE_DATA = {
    '': ['resources/*.txt', 'resources/*.json', 'resources/*.dat'],
}
AUTHOR = data_utils.__author__
AUTHOR_EMAIL = 'jgu@dytechlab.com'
URL = 'http://gitlab.dtl/jgu/data_utils'


REQUIRES = []
with open('requirements.txt', 'r') as ifile:
    for line in ifile:
        REQUIRES.append(line.strip())
VERSION = data_utils.__version__
DESCRIPTION = 'DTL internal data projects utilities'
KEYWORDS = 'data processing utility'
LONG_DESC = data_utils.__doc__

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESC,
    url=URL,
    keywords=KEYWORDS,
    entry_points={
        'console_scripts': [
            'start_data_proj = libstarter.main:main',
        ]
    },
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    include_package_data=True,
    install_requires=REQUIRES,
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
    ],
)
