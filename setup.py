# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in prestashop_erpnext_connector/__init__.py
from prestashop_erpnext_connector import __version__ as version

setup(
	name='prestashop_erpnext_connector',
	version=version,
	description='App To Synchronize Data From Erpnext To Prestashop',
	author='webkul',
	author_email='demo@webkul.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
