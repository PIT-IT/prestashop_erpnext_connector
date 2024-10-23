# Copyright(c) 2010-present, Webkul Software Pvt Ltd
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Prestashop Erpnext Connector"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
					"name": "Synchronization",
					"description": _("Bulk Synchronization To Export Data."),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Instance",
					"description": _("Instance To Connect With Prestashop."),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "OrderMapping",
					"description": _("Order Mappings with prestashop."),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "CustomerMapping",
					"description": _("Customer Mappings with prestashop."),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "CategoryMapping",
					"description": _("Category Mappings with prestashop."),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "AttributeMapping",
					"description": _("Attribute Mappings with prestashop."),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "AttributeValueMapping",
					"description": _("Attribute Value Mappings with prestashop."),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "ProductMapping",
					"description": _("Product Mappings with prestashop."),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "ProductVariantMapping",
					"description": _("Product Variant Mappings with prestashop."),
					"onboard": 1,
				},
			]
		},
	]
