#!/usr/bin/env python
from setuptools import setup, find_packages
import os

setup(name='wl-daemon',
      version='0.1',
      description='Whitelisting Daemon',
      author='CommerceBlock',
      author_email='lawrence@commerceblock.com',
      url='http://github.com/commerceblock/wl-daemon',
      packages=find_packages(),
      scripts=[],
      include_package_data=True,
      data_files=[],
)
