# -*- coding: utf-8 -*-
# Copyright(c) 2010-present, Webkul Software Pvt Ltd
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
import prestashop_erpnext_connector
from prestashop_erpnext_connector.prestapi.prestapi import PrestaShopWebService,PrestaShopWebServiceDict,PrestaShopWebServiceError,PrestaShopAuthenticationError
from .category import addto_prestashop_merge

@frappe.whitelist()
def export_attributes():
	message=""
	extra_message=""
	count = 0
	try:
		check_active_id = frappe.db.sql("""
				select `api_url`,`api_key`
				from `tabInstance` where active=1 limit 1""")
		if check_active_id:
			url = check_active_id[0][0]
			key = check_active_id[0][1]
			try:
				prestashop = PrestaShopWebServiceDict(url,key)
				check_categories = frappe.db.sql("""
				select `name`,`attribute_name`
				from `tabItem Attribute` WHERE `name` Not in (select `erpnext_id` from `tabAttributeMapping`) limit 1000""")
				for l in check_categories:
					get_response = create_dimension_type(prestashop, l[0],l[1])
					p_cat_id = get_response[0]
					if p_cat_id:
						count+= 1
					else:
						extra_message = '\r\n' + extra_message + get_response[1]
				if not extra_message:
					extra_message = "%s Attribute(s) has been Exported to PrestaShop."%(count)
			except Exception as e:
				message='\r\n'+message+str(e)
		else:
			message = 'No Connection Found, Please Create/Active A Connection'
	except Exception as e:
		message = 'Error:%s'%str(e)
	finally:
		message = message + '<br />' + extra_message
	frappe.msgprint(message)


def create_dimension_type(prestashop, erpnext_id, name):
	try:
		add_data = prestashop.get('product_options', options={'schema': 'blank'})
	except Exception as e:
		return [0,'\r\Attribute Id:%s ;Error in Creating blank schema for categories.Detail : %s'%(str(erpnext_id),str(e)),False]
	if add_data:
		add_data['product_option'].update({
									'group_type': 'select',
									'position':'0'
								})
		if type(add_data['product_option']['name']['language']) == list:
			for i in range(len(add_data['product_option']['name']['language'])):
				add_data['product_option']['name']['language'][i]['value'] = name
				add_data['product_option']['public_name']['language'][i]['value'] = name
		else:
			add_data['product_option']['name']['language']['value'] = name
			add_data['product_option']['public_name']['language']['value'] = name
		try:
			returnid = prestashop.add('product_options', add_data)
		except Exception as e:
			return [0,' Error in creating Dimension Type(ID: %s).%s'%(str(erpnext_id),str(e))]
		if returnid:
			frappe.new_doc("AttributeMapping").update({'erpnext_id':erpnext_id,'title':erpnext_id,'ecomm_id':returnid,'created_by':'erpnext'}).insert()
			addto_prestashop_merge(prestashop, 'erpnext_attributes_merges', {'erpnext_id':erpnext_id, 'presta_id':returnid})
			return [1,'',returnid]
