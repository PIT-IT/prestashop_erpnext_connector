# -*- coding: utf-8 -*-
# Copyright(c) 2010-present, Webkul Software Pvt Ltd
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
import prestashop_erpnext_connector
from prestashop_erpnext_connector.prestapi.prestapi import PrestaShopWebService,PrestaShopWebServiceDict,PrestaShopWebServiceError,PrestaShopAuthenticationError

	
def _get_link_rewrite(string):
	if type(string)!=str:
		string =string.encode('ascii','ignore')
		string=str(string)
	import re
	string=re.sub('[^A-Za-z0-9]+',' ',string)
	string=string.replace(' ','-').replace('/','-')
	string=string.lower()
	return string

@frappe.whitelist()
def export_categories():
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
				select `name`,`item_group_name`,`parent_item_group`
				from `tabItem Group` WHERE `name` Not in (select `erpnext_id` from `tabCategoryMapping`) and `name`!='All Item Groups' limit 1000""")
				for l in check_categories:
					get_response = sync_categories(prestashop, l[0],l[1],l[2])
					p_cat_id = get_response[0]
					if p_cat_id:
						count+= 1
					else:
						extra_message = '\r\n' + extra_message + get_response[1]
				if not extra_message:
					extra_message = "%s Category(s) has been Exported to PrestaShop."%(count)
			except Exception as e:
				message='\r\n'+message+str(e)
		else:
			message = 'No Connection Found, Please Create A New Connection'
	except Exception as e:
		message = 'Error:%s'%str(e)
	finally:
		message = message + '<br />' + extra_message
	frappe.msgprint(message)


def sync_categories(prestashop, id_erpnext, name, parent_id):
	check_category = frappe.db.sql("""
				select `ecomm_id`
				from `tabCategoryMapping` WHERE `erpnext_id`='%s' limit 1"""%id_erpnext)
	
	if not check_category:
		name = name
		if parent_id and parent_id!='All Item Groups':
			check_parent = frappe.db.sql("""
				select `name`,`item_group_name`,`parent_item_group`
				from `tabItem Group` WHERE `name`='%s' limit 1"""%parent_id)
			if check_parent:
				p_cat_id = sync_categories(prestashop, check_parent[0][0],check_parent[0][1],check_parent[0][2])[0]
		else:
			get_response= create_categories(prestashop, id_erpnext, name, '0', '2')
			p_cat_id = get_response[2] if get_response[0] else 0
			return [p_cat_id,get_response[1]]
		get_response = create_categories(prestashop, id_erpnext, name, '0', p_cat_id)
		p_cat_id = get_response[2] if get_response[0] else 0
		return [p_cat_id,get_response[1]]
	else:
		return [check_category[0][0],'']

def create_categories(prestashop, erpnext_id, name, is_root_category, id_parent, link_rewrite='None', description='None', meta_description='None', meta_keywords='None', meta_title='None'):
	try:
		cat_data = prestashop.get('categories', options={'schema': 'blank'})
	except Exception as e:
		return [0,'\r\nCategory Id:%s ;Error in Creating blank schema for categories.Detail : %s'%(str(erpnext_id),str(e)),False]
	if cat_data:
		if type(cat_data['category']['name']['language']) == list:
			for i in range(len(cat_data['category']['name']['language'])):
				cat_data['category']['name']['language'][i]['value'] = name
				cat_data['category']['link_rewrite']['language'][i]['value'] = _get_link_rewrite(name)
				cat_data['category']['description']['language'][i]['value'] = description
				cat_data['category']['meta_description']['language'][i]['value'] = meta_description
				cat_data['category']['meta_keywords']['language'][i]['value'] = meta_keywords
				cat_data['category']['meta_title']['language'][i]['value'] = name
		else:
			cat_data['category']['name']['language']['value'] = name
			cat_data['category']['link_rewrite']['language']['value'] = _get_link_rewrite(name)
			cat_data['category']['description']['language']['value'] = description
			cat_data['category']['meta_description']['language']['value'] = meta_description
			cat_data['category']['meta_keywords']['language']['value'] = meta_keywords
			cat_data['category']['meta_title']['language']['value'] = name
		cat_data['category']['is_root_category'] = is_root_category
		cat_data['category']['id_parent'] = id_parent
		cat_data['category']['active'] = 1
		try:
			returnid = prestashop.add('categories', cat_data)
		except Exception as e:
			return [0, '\r\nCategory Id:%s ;Error in creating Category(s).Detail : %s'%(str(erpnext_id), str(e)), False]
		if returnid:
			frappe.new_doc("CategoryMapping").update({'erpnext_id':erpnext_id,'title':erpnext_id,'ecomm_id':returnid,'created_by':'erpnext'}).insert()
			addto_prestashop_merge(prestashop, 'erpnext_category_merges', {'erpnext_id':erpnext_id, 'presta_id':returnid})
			return [1,'',returnid]


def addto_prestashop_merge(prestashop, resource, data):
	try:
		resource_data = prestashop.get(resource, options={'schema': 'blank'})
	except Exception as e:
		return [0,' Error in Creating blank schema for resource.']
	if resource_data:
		if resource == 'erpnext_attributes_merges':
			resource_data['erpnext_attributes_merge'].update({
				'erpnext_attribute_id':data['erpnext_id'],
				'prestashop_attribute_id':data['presta_id'],
				'created_by':'erpnext',
				})
			try:
				returnid = prestashop.add(resource, resource_data)
				return [1, '']
			except Exception as e:
				return [0,' Error in Creating Entry in Prestashop for Attribute.']
		if resource == 'erpnext_attribute_values_merges':
			resource_data['erpnext_attribute_values_merge'].update({
				'erpnext_attribute_id':data['erpnext_attribute_id'],
				'erpnext_attribute_value_id':data['erpnext_id'],
				'prestashop_attribute_value_id':data['presta_id'],
				'prestashop_attribute_id':data['presta_attribute_id'],
				'created_by':'erpnext',
				})
			try:
				returnid = prestashop.add(resource, resource_data)
				return [1, '']
			except Exception as e:
				return [0, ' Error in Creating Entry in Prestashop for Attribute Value.']
		if resource == 'erpnext_product_merges':
			resource_data['erpnext_product_merge'].update({
				'erpnext_product_id':data['erpnext_id'],
				'erpnext_template_id':data['erpnext_temp_id'],
				'prestashop_product_id':data['presta_id'],
				'prestashop_product_attribute_id':data.get('prestashop_product_attribute_id','0'),
				'created_by':'erpnext',
				})
			try:
				returnid = prestashop.add(resource, resource_data)
				return [1, '']
			except Exception as e:
				return [0, ' Error in Creating Entry in Prestashop for Product.']
		if resource == 'erpnext_product_template_merges':
			resource_data['erpnext_product_template_merge'].update({
				'erpnext_template_id':data['erpnext_id'],
				'presta_product_id':data['presta_id'],
				'created_by':'erpnext',
				})
			try:
				returnid = prestashop.add(resource, resource_data)
				return [1, '']
			except Exception as e:
				return [0, ' Error in Creating Entry in Prestashop for Template.']
		if resource == 'erpnext_category_merges':
			resource_data['erpnext_category_merge'].update({
				'erpnext_category_id':data['erpnext_id'],
				'prestashop_category_id':data['presta_id'],
				'created_by':'erpnext',
				})
			try:
				returnid = prestashop.add(resource, resource_data)
				return [1, '']
			except Exception as e:
				return [0, ' Error in Creating Entry in Prestashop for Category.']
		if resource=='erpnext_customer_merges':
			resource_data['erpnext_customer_merge'].update({
				'erpnext_customer_id':data['erpnext_id'],
				'prestashop_customer_id':data['presta_id'],
				'created_by':'erpnext',
				})
			try:
				returnid = prestashop.add(resource, resource_data)
				return [1, '']
			except Exception as e:
				return [0, ' Error in Creating Entry in Prestashop for Customer.']
		if resource == 'erpnext_address_merges':
			resource_data['erpnext_address_merge'].update({
				'erpnext_address_id':data['erpnext_id'],
				'prestashop_address_id':data['presta_id'],
				'id_customer':data['presta_cust_id'],
				'created_by':'erpnext',
				})
			try:
				returnid = prestashop.add(resource, resource_data)
				return [1, '']
			except Exception as e:
				return [0, ' Error in Creating Entry in Prestashop for Customer.']
	return [0, ' Unknown Error in Creating Entry in Prestashop.']

