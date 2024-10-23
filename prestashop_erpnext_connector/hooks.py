# -*- coding: utf-8 -*-
# Copyright(c) 2010-present, Webkul Software Pvt Ltd
# For license information, please see license.txt

from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "presatshop_erpnext_connector"
app_title = "Prestashop Erpnext Connector"
app_publisher = "Webkul Software Pvt. Ltd."
app_description = "App to export data from Erpnext to Prestashop"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "sales@webkul.com"
app_license = "See license.txt"

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Item": {
		"on_update": "prestashop_erpnext_connector.override.on_update",
	},
    "Payment Entry": {
		"on_submit": "prestashop_erpnext_connector.override.on_payment_submit",
	},
    "Delivery Note": {
		"on_submit": "prestashop_erpnext_connector.override.on_delivery_submit",
	},
    "Sales Order": {
		"on_cancel": "prestashop_erpnext_connector.override.on_sale_cancel",
	},
	#  "Stock Ledger Entry": {
	# 	"on_stock_update": "prestashop_erpnext_connector.override.on_stock_update",
	# },
	 "Bin": {
		"on_update": "prestashop_erpnext_connector.override.on_stock_update",
	},
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"prestashop_erpnext_connector.tasks.all"
# 	],
# 	"daily": [
# 		"prestashop_erpnext_connector.tasks.daily"
# 	],
# 	"hourly": [
# 		"prestashop_erpnext_connector.tasks.hourly"
# 	],
# 	"weekly": [
# 		"prestashop_erpnext_connector.tasks.weekly"
# 	]
# 	"monthly": [
# 		"prestashop_erpnext_connector.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "prestashop_erpnext_connector.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "prestashop_erpnext_connector.event.get_events"
# }

