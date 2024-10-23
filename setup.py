# -*- coding: utf-8 -*-
# Copyright(c) 2010-present, Webkul Software Pvt Ltd
# For license information, please see license.txt

from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in prestashop_erpnext_connector/__init__.py
from prestashop_erpnext_connector import __version__ as version

setup(
	name='prestashop_erpnext_connector',
	version=version,
	description='App To Synchronize Data From Erpnext To Prestashop',
	author='Webkul Software PVT. LTD.',
	author_email='sales@webkul.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
