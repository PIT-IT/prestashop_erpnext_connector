# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
import prestashop_erpnext_connector
from prestashop_erpnext_connector.prestapi.prestapi import PrestaShopWebService,PrestaShopWebServiceDict,PrestaShopWebServiceError,PrestaShopAuthenticationError



class Synchronization(Document):
	pass
