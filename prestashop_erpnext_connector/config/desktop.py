# -*- coding: utf-8 -*-
# Copyright(c) 2010-present, Webkul Software Pvt Ltd
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "prestashop_erpnext_connector",
			"type": "module",
			"category": "Modules",
			"color": "#3498db",
			"icon": "octicon octicon-repo",
			"description": "Synchronize Data like products,stock,categories from erpnext to prestashop",
			"label": _("Prestashop Erpnext Connector")
		}
	]
