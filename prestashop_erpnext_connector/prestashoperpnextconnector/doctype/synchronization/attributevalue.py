# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
import prestashop_erpnext_connector
from prestashop_erpnext_connector.prestapi.prestapi import PrestaShopWebService,PrestaShopWebServiceDict,PrestaShopWebServiceError,PrestaShopAuthenticationError
from .category import addto_prestashop_merge

@frappe.whitelist()
def export_attributevalues():
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
				check_attribute_values = frappe.db.sql("""
				select itv.`name`,itv.`attribute_value`,itv.`parent`,it.`ecomm_id`
				from `tabItem Attribute Value` itv JOIN 
				`tabAttributeMapping` it ON(it.`erpnext_id`=itv.`parent`) WHERE itv.`name` Not in (select `erpnext_id` from `tabAttributeValueMapping`) limit 1000""")
				for l in check_attribute_values:
					get_response = create_dimension_options(prestashop, l[0],l[1], l[2],l[3])
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


def create_dimension_options(prestashop, erpnext_id, name, erpnext_attr_id, ecomm_attr_id):
	try:
		add_value = prestashop.get('product_option_values', options={'schema': 'blank'})
	except Exception as e:
		return [0,'\rAttribute Id:%s ;Error in Creating blank schema for categories.Detail : %s'%(str(erpnext_id),str(e)),False]
	if add_value:
		add_value['product_option_value'].update({
									'id_attribute_group': ecomm_attr_id,
									'position':'0'
								})
		if type(add_value['product_option_value']['name']['language']) == list:
			for i in range(len(add_value['product_option_value']['name']['language'])):
				add_value['product_option_value']['name']['language'][i]['value'] = name
		else:
			add_value['product_option_value']['name']['language']['value'] = name
		try:
			returnid = prestashop.add('product_option_values', add_value)
		except Exception as e:
			return [0, ' Error in creating Dimension Option(ID: %s).%s'%(str(erpnext_id),str(e))]
		if returnid:
			frappe.new_doc("AttributeValueMapping").update({'ecomm_attribute_id':ecomm_attr_id,
			'erpnext_attribute_id':erpnext_attr_id,'erpnext_id':erpnext_id,'title':erpnext_id,'ecomm_id':returnid,'created_by':'erpnext'}).insert()
			addto_prestashop_merge(prestashop, 'erpnext_attribute_values_merges', {'erpnext_id':erpnext_id, 'presta_id':returnid,
			'erpnext_attribute_id':erpnext_attr_id,
			'presta_attribute_id':ecomm_attr_id})
			return [1,'',returnid]
