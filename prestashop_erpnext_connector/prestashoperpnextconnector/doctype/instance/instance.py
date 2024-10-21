# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
import prestashop_erpnext_connector
from prestashop_erpnext_connector.prestapi.prestapi import PrestaShopWebService,PrestaShopWebServiceDict,PrestaShopWebServiceError,PrestaShopAuthenticationError

class Instance(Document):
	def before_save(self, *args, **kwargs):
		if self.get("__islocal") or not self.get("name"):
			check_active_id = frappe.db.sql("""
				select `api_url`,`api_key`
				from `tabInstance` limit 1""")
			if check_active_id:	
				frappe.throw(_("Only One Connection Allowed"))
	

@frappe.whitelist()
def test_connection():
	flag=0
	message="<h2>Connected successfully...you can start syncing data now.</h2>"
	extra_message=""
	try:
		check_active_id = frappe.db.sql("""
				select `api_url`,`api_key`
				from `tabInstance` limit 1""")
		if check_active_id:
			url = check_active_id[0][0]
			key = check_active_id[0][1]
			try:
				prestashop = PrestaShopWebServiceDict(url,key)
				languages = prestashop.get("languages",options={'filter[active]':'1',})
			except Exception as e:
				message='Connection Error: '+str(e)+'\r\n'
				try:
					import requests
					from lxml import etree
					client = requests.Session()
					client.auth=(key, '')
					response=client.request('get',url)
					msg_tree=etree.fromstring(response.content)
					for element in msg_tree.xpath("//message"):
						message=message+element.text
				except Exception as e:
					message='\r\n'+message+str(e)
		else:
			message = 'No Connection Instance Found On Server, Please save the details First'
	except Exception as e:
		message = 'Error:%s'%str(e)
	finally:
		message = message + '<br />' + extra_message
	frappe.msgprint(message)
