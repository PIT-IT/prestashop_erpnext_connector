# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "presatshop_erpnext_connector"
app_title = "Prestashop Erpnext Connector"
app_publisher = "Webkul"
app_description = "App for webkul modules"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "test@webkul.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/prestashop_erpnext_connector/css/prestashop_erpnext_connector.css"
# app_include_js = "/assets/prestashop_erpnext_connector/js/prestashop_erpnext_connector.js"

# include js, css files in header of web template
# web_include_css = "/assets/prestashop_erpnext_connector/css/prestashop_erpnext_connector.css"
# web_include_js = "/assets/prestashop_erpnext_connector/js/prestashop_erpnext_connector.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "prestashop_erpnext_connector.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "prestashop_erpnext_connector.install.before_install"
# after_install = "prestashop_erpnext_connector.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "prestashop_erpnext_connector.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

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

