#!/usr/bin/env python
from __future__ import absolute_import, print_function

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from src import proxypool

NAME = 'proxypool'
PACKAGES = [
    'proxypool',
]
PACKAGE_DATA = {
    'proxypool': ['resources/*.json']
}
AUTHOR = proxypool.__author__
AUTHOR_EMAIL = proxypool.__author_email__
URL = 'https://github.com/franklingu/proxypool'


REQUIRES = []
with open('requirements.txt', 'r') as ifile:
    for line in ifile:
        REQUIRES.append(line.strip())
VERSION = proxypool.__version__
DESCRIPTION = 'A proxy poll: get free and high quality proxies'
KEYWORDS = 'proxy pool free collector'
LONG_DESC = proxypool.__doc__

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESC,
    url=URL,
    keywords=KEYWORDS,
    license='MIT',
    package_dir={'': 'src'},
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    include_package_data=True,
    install_requires=REQUIRES,
    python_requires='>=3.5, <4',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
)
