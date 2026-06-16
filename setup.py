#!/usr/bin/env python3

from setuptools import find_packages, setup


setup(
    name='fuo_qqmusic',
    version='1.0.16',
    description='feeluown qqmusic plugin',
    author='Cosven',
    author_email='yinshaowen241@gmail.com',
    # find_packages() picks up fuo_qqmusic/ and fuo_qqmusic/i18n/
    # (the previous hard-coded 'fuo_qqmusic' list missed the i18n
    # subpackage, which broke pip-install of this plugin).
    packages=find_packages(include=['fuo_qqmusic', 'fuo_qqmusic.*']),
    package_data={
        '': ['assets/*.svg',]
    },
    url='https://github.com/feeluown/feeluown-qqmusic',
    keywords=['feeluown', 'plugin', 'qqmusic'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],
    install_requires=[
        'feeluown>=4.1.13',
        'requests',
        'marshmallow>=3.13.0,<4.0.0'
    ],
    entry_points={
        'fuo.plugins_v1': [
            'qqmusic = fuo_qqmusic',
        ]
    },
)
