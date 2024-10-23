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
from .category import sync_categories,_get_link_rewrite
from erpnext.stock.utils import get_stock_balance
from frappe.utils import flt, cstr, nowdate, nowtime
import base64


@frappe.whitelist()
def export_products():
	message=""
	extra_message=""
	count = 0
	try:
		check_active_id = frappe.db.sql("""
				select `api_url`,`api_key`,`warehouse`
				from `tabInstance` where active=1 limit 1""")
		if check_active_id:
			url = check_active_id[0][0]
			key = check_active_id[0][1]
			warehouse = check_active_id[0][2]
			try:
				prestashop = PrestaShopWebServiceDict(url,key)
				product_schema = prestashop.get('products', options = {'schema':'blank'})
				combination_schema = prestashop.get('combinations', options= {'schema':'blank'})
				check_products = frappe.db.sql("""
				select `name`,`variant_of`,`has_variants` from `tabItem` WHERE `name` Not in (select `erpnext_variant_id` from `tabProductVariantMapping`)and is_stock_item= 1 limit 1000""")
				for check in check_products:
					is_variant =False
					if check[1]:
						name = check[1]
						is_variant = True
					else:
						name = check[0]
					itemObj = frappe.get_doc("Item", name)
					quantity = get_stock_balance(itemObj.name,warehouse,nowdate())
					get_response = export_template(prestashop, itemObj, product_schema)
					if get_response['status']:
						ecomm_id = get_response['prestashop_product_id']
						comb_id = 0
						if get_response['create_mapping']:
							count+= 1
							frappe.new_doc("ProductMapping").update({'erpnext_id':itemObj.name,'title':itemObj.name,'ecomm_id':ecomm_id,'created_by':'erpnext',
							'is_sync':1}).insert()
							addto_prestashop_merge(prestashop, 'erpnext_product_template_merges', {'erpnext_id':itemObj.name, 'presta_id':ecomm_id})
						if is_variant and itemObj.variant_based_on=='Item Attribute':
							itemVariantObj = frappe.get_doc("Item", check[0])
							quantity = get_stock_balance(itemVariantObj.name,warehouse, nowdate())
							check_response = check_attributes(prestashop,ecomm_id, itemVariantObj, itemObj,combination_schema)
							if check_response['status']:
								comb_id = check_response['prestashop_comb_id']
								frappe.new_doc("ProductVariantMapping").update({'erpnext_id':itemObj.name,'title':itemObj.name,'ecomm_id':ecomm_id,'created_by':'erpnext',
								'erpnext_variant_id':itemVariantObj.name,'ecomm_variant_id':comb_id,
								'is_sync':1}).insert()
								addto_prestashop_merge(prestashop, 'erpnext_product_merges', {'erpnext_id':itemVariantObj.name, 'presta_id':ecomm_id,
								'erpnext_temp_id':itemObj.name,
								'prestashop_product_attribute_id':comb_id})
						elif not check[2] or itemObj.variant_based_on!='Item Attribute' :
							frappe.new_doc("ProductVariantMapping").update({'erpnext_id':itemObj.name,'title':itemObj.name,'ecomm_id':ecomm_id,'created_by':'erpnext',
							'erpnext_variant_id':itemObj.name,'ecomm_variant_id':'0',
							'is_sync':1}).insert()
							addto_prestashop_merge(prestashop, 'erpnext_product_merges', {'erpnext_id':itemObj.name, 'presta_id':ecomm_id,
							'erpnext_temp_id': itemObj.name,
							'prestashop_product_attribute_id':'0'
							})
						quantity_response = update_quantity_prestashop(prestashop,ecomm_id,comb_id,quantity)
						if quantity_response[0]==0:
							print("Issue in Updating Stock%r",quantity_response[1])
					else:
						extra_message+= get_response['error']
				if not extra_message:
					extra_message = "%s Product(s) has been Exported to PrestaShop."%(count)
			except Exception as e:
				message='\r\n'+message+str(e)
		else:
			message = 'No Connection Found, Please Create/Active A Connection'
	except Exception as e:
		message = 'Error:%s'%str(e)
	finally:
		message = message + '<br />' + extra_message
	frappe.msgprint(message)


def check_attributes(prestashop, ecomm_id, itemVariantObj, itemObj, combination_schema):
	status = False
	prestashop_comb_id = 0
	error = ''
	price_extra = float(itemVariantObj.standard_rate) - float(itemObj.standard_rate)
	presta_dim_list = []
	for value_id in itemVariantObj.attributes:
		attribute_value = value_id.attribute_value
		attribute = value_id.attribute
		mapping = frappe.db.sql("""
			select avm.`ecomm_id`
			from `tabAttributeValueMapping` avm INNER JOIN
			`tabItem Attribute Value` iav On (avm.`erpnext_id`= iav.`name`) WHERE iav.`attribute_value`='%s' and iav.`parent`= '%s' limit 1"""%(attribute_value,attribute))
		if mapping:
			presta_dim_list.append({'id':str(mapping[0][0])})
		else:
			frappe.throw('Please Map All Dimentions(Attributes and Attribute Values) First And than Try To Update Product')
	combination_schema['combination']['associations']['product_option_values']['product_option_value'] = presta_dim_list
	combination_schema['combination'].update({
							'weight':str(itemVariantObj.weight_per_unit or ''),
							'reference':itemVariantObj.item_code or '',
							'wholesale_price':str(round(itemVariantObj.last_purchase_rate,6)),
							'price':str(round(price_extra,6)),
							'quantity':'0',
							'default_on':'0',
							'id_product':str(ecomm_id),
							'minimal_quantity':'1',
							})
	for barcode in itemVariantObj.barcodes:
			if barcode.barcode_type=='EAN':
				combination_schema['combination']['ean13'] = barcode.barcode
	if itemVariantObj.image:
		image_id = create_images(prestashop, itemVariantObj.name, itemVariantObj.image, 'Item', ecomm_id)
		if image_id:
			combination_schema['combination']['associations']['images']['image']['id'] = str(image_id)
	try:
		prestashop_comb_id = prestashop.add('combinations',combination_schema)
		status = True
	except Exception as e:
		print("-exception_raised---creating combination -- adding_product_schema --%r",combination_schema)
		error = str(e)
	return{
		'status': status,
		'error' : error,
		'prestashop_comb_id':prestashop_comb_id
	}


def export_template(prestashop , template_data, product_schema):
	status = False
	error = ''
	prestashop_product_id = 0
	ps_categ_id = ''
	mapping = frappe.db.sql("""
				select `ecomm_id`
				from `tabProductMapping` WHERE `erpnext_id`='%s' limit 1"""%template_data.name)
	if mapping:
		return {
			'status':True,
			'error':error,
			'prestashop_product_id':mapping[0][0],
			'create_mapping':False
		}
	if product_schema:
		category_data = frappe.db.sql("""
				select `item_group_name`,`parent_item_group`
				from `tabItem Group` WHERE `name`='%s' limit 1"""%template_data.item_group)
		if category_data:
			ps_categ_id = sync_categories(prestashop,template_data.item_group,category_data[0][0],category_data[0][1]
		)[0]
		product_schema['product'].update({
						'price': str(round(float(template_data.standard_rate),6)),
						'active':'1',
						'redirect_type':'404',
						'minimal_quantity':'1',
						'available_for_order':'1',
						'show_price':'1',
						'state':'1',
						'default_on':'1',
						'reference': template_data.item_code,
						'out_of_stock':'2',
						'condition':'new',
						'id_category_default':str(ps_categ_id),
						'weight':str(template_data.weight_per_unit or ''),
					})
		for barcode in template_data.barcodes:
			if barcode.barcode_type=='EAN':
				product_schema['product']['ean13'] = barcode.barcode
		if template_data.last_purchase_rate:
			product_schema['product']['wholesale_price'] = str(round(float(template_data.last_purchase_rate),6))
		if type(product_schema['product']['name']['language']) == list:
			for i in range(len(product_schema['product']['name']['language'])):
				product_schema['product']['name']['language'][i]['value'] = template_data.item_name
				product_schema['product']['link_rewrite']['language'][i]['value'] = _get_link_rewrite(template_data.item_name)
				product_schema['product']['description']['language'][i]['value'] = template_data.description
		else:
			product_schema['product']['name']['language']['value'] = template_data.item_name
			product_schema['product']['link_rewrite']['language']['value'] = _get_link_rewrite(template_data.item_name)
			product_schema['product']['description']['language']['value'] = template_data.description
		if type(product_schema['product']['associations']['categories']['category'])== list:
				product_schema['product']['associations']['categories']['category'] = product_schema['product']['associations']['categories']['category'][0]
		product_schema['product']['associations']['categories']['category']['id'] = str(ps_categ_id)
		pop_attr = product_schema['product']['associations'].pop('combinations',None)
		a1 = product_schema['product']['associations'].pop('images',None)
		a2 = product_schema['product'].pop('position_in_category',None)
		try:
			prestashop_product_id = prestashop.add('products', product_schema)
			status = True
			if template_data.image:
				create_images(prestashop, template_data.name, template_data.image, 'Item', prestashop_product_id)
		except Exception as e:
			print("---exception raised while export template--- %r",product_schema)
			error = str(e)
	return{
		'status': status,
		'error' : error,
		'prestashop_product_id':prestashop_product_id,
		'create_mapping':True
		}

@frappe.whitelist()
def update_products():
	message=""
	extra_message=""
	count = 0
	try:
		check_active_id = frappe.db.sql("""
				select `api_url`,`api_key`,`ps_lang`,`warehouse`
				from `tabInstance` where active=1 limit 1""")
		if check_active_id:
			url = check_active_id[0][0]
			key = check_active_id[0][1]
			ps_lang = check_active_id[0][2]
			warehouse = check_active_id[0][3]
			try:
				prestashop = PrestaShopWebServiceDict(url,key)
				check_products = frappe.db.sql("""
				select `erpnext_id`,`ecomm_id`,`ecomm_variant_id`,`erpnext_variant_id` from `tabProductVariantMapping` where is_sync=0 limit 1000""")
				for check in check_products:
					itemObj = frappe.get_doc("Item", check[0])
					ecomm_id = check[1]
					comb_id = check[2]
					if int(comb_id)==0:
						get_response = update_template(prestashop, itemObj,ecomm_id, ps_lang)
						quantity = get_stock_balance(itemObj.name,warehouse, nowdate())
					else:
						itemObj = frappe.get_doc("Item", check[0])
						get_response = update_template(prestashop, itemObj,ecomm_id, ps_lang)
						itemVariantObj = frappe.get_doc("Item", check[3])
						get_response = update_attributes(prestashop,ecomm_id,comb_id,itemVariantObj, itemObj)
						quantity = get_stock_balance(itemVariantObj.name,warehouse, nowdate())
					if get_response['status']:
						quantity_response = update_quantity_prestashop(prestashop,ecomm_id,comb_id,quantity)
						if quantity_response[0]==0:
							print("Issue in Updating Stock%r",quantity_response[1])
						count+= 1
					else:
						extra_message+= get_response['error']
				if not extra_message:
					extra_message = "%s Product(s) has been Updated to PrestaShop."%(count)
			except Exception as e:
				message='\r\n'+message+str(e)
		else:
			message = 'No Connection Found, Please Create/Active A Connection'
	except Exception as e:
		message = 'Error:%s'%str(e)
	finally:
		message = message + '<br />' + extra_message
	frappe.msgprint(message)

def update_template(prestashop , template_data, ecomm_id, ps_lang):
	status = False
	error = ''
	ps_categ_id = ''
	product_schema = False
	mapping = frappe.db.sql("""
				select `ecomm_id`
				from `tabProductMapping` WHERE `erpnext_id`='%s' and is_sync=0 limit 1"""%template_data.name)
	if mapping:
		try:
			product_schema = prestashop.get('products', ecomm_id)
		except Exception as e:
			error = str(e)
		if product_schema:
			category_data = frappe.db.sql("""
					select `item_group_name`,`parent_item_group`
					from `tabItem Group` WHERE `name`='%s' limit 1"""%template_data.item_group)
			if category_data:
				ps_categ_id = sync_categories(prestashop,template_data.item_group,category_data[0][0],category_data[0][1]
			)[0]
			product_schema['product'].update({
							'price': str(round(float(template_data.standard_rate),6)),
							'reference': template_data.item_code,
							'id_category_default':str(ps_categ_id),
							'weight':str(template_data.weight_per_unit or ''),
						})
			for barcode in template_data.barcodes:
				if barcode.barcode_type=='EAN':
					product_schema['product']['ean13'] = barcode.barcode
			if template_data.last_purchase_rate:
				product_schema['product']['wholesale_price'] = str(round(float(template_data.last_purchase_rate),6))
			if type(product_schema['product']['name']['language']) == list:
				for i in range(len(product_schema['product']['name']['language'])):
					if int(product_schema['product']['name']['language'][i]['attrs']['id'])==int(ps_lang):
						product_schema['product']['name']['language'][i]['value'] = template_data.item_name
						product_schema['product']['description']['language'][i]['value'] = template_data.description
			else:
				product_schema['product']['name']['language']['value'] = template_data.item_name
				product_schema['product']['description']['language']['value'] = template_data.description
			if type(product_schema['product']['associations']['categories']['category'])== list:
				product_schema['product']['associations']['categories']['category'] = product_schema['product']['associations']['categories']['category'][0]
			product_schema['product']['associations']['categories']['category']['id'] = str(ps_categ_id)
			a1 = product_schema['product'].pop('position_in_category',None)
			a2 = product_schema['product'].pop('manufacturer_name',None)
			a3 = product_schema['product'].pop('quantity',None)
			a4 = product_schema['product'].pop('type',None)
			try:
				prestashop_product_id = prestashop.edit('products',ecomm_id,product_schema)
				status = True
				frappe.db.sql("""update `tabProductMapping`
					set is_sync =1 where erpnext_id='%s'"""%template_data.name)
			except Exception as e:
				print("---exception raised while export template--- %r",product_schema)
				error = str(e)
			if 'image' not in product_schema['product']['associations']['images']:
				if template_data.image:
					create_images(prestashop, template_data.name, template_data.image, 'Item', ecomm_id)
	else:
		status = True
	return{
		'status': status,
		'error' : error
		}

def update_attributes(prestashop, ecomm_id, ecomm_combination_id, itemVariantObj, itemObj):
	status = False
	error = ''
	combination_schema = False
	try:
		combination_schema = prestashop.get('combinations',ecomm_combination_id)
	except Exception as e:
		status = False
		error = str(e)
	if combination_schema:
		price_extra = float(itemVariantObj.standard_rate) - float(itemObj.standard_rate)
		presta_dim_list = []
		for value_id in itemVariantObj.attributes:
			attribute_value = value_id.attribute_value
			attribute = value_id.attribute
			mapping = frappe.db.sql("""
					select avm.`ecomm_id`
					from `tabAttributeValueMapping` avm INNER JOIN
					`tabItem Attribute Value` iav On (avm.`erpnext_id`= iav.`name`) WHERE iav.`attribute_value`='%s' and iav.`parent`= '%s' limit 1"""%(attribute_value,attribute))
			if mapping:
				presta_dim_list.append({'id':str(mapping[0][0])})
			else:
				frappe.throw('Please Map All Dimentions(Attributes and Attribute Values')
		a1 = combination_schema['combination']['associations']['product_option_values'].pop('product_option_value')
		combination_schema['combination']['associations']['product_option_values']['product_option_value'] = presta_dim_list
		combination_schema['combination'].update({
								'weight':str(itemVariantObj.weight_per_unit or ''),
								'reference':itemVariantObj.item_code or '',
								'wholesale_price':str(round(itemVariantObj.last_purchase_rate,6)),
								'price':str(round(price_extra,6)),
								'id_product':str(ecomm_id),
								})
		if itemVariantObj.image:
				if 'image' not in combination_schema['combination']['associations']['images']:
					image_id = create_images(prestashop, itemVariantObj.name, itemVariantObj.image, 'Item', ecomm_id)
					combination_schema['combination']['associations'].pop('images',False)
					if image_id:
						combination_schema['combination']['associations']['images']={'image':{'id':str(image_id)}}
		for barcode in itemVariantObj.barcodes:
			if barcode.barcode_type=='EAN':
				combination_schema['combination']['ean13'] = barcode.barcode
		try:
			prestashop_comb_id = prestashop.edit('combinations',ecomm_combination_id,combination_schema)
			status = True
			frappe.db.sql("""update `tabProductVariantMapping`
				set is_sync =1 where erpnext_variant_id='%s'"""%itemVariantObj.name)
		except Exception as e:
			print("-exception_raised---creating combination -- adding_product_schema --%r",combination_schema)
			error = str(e)
	return{
		'status': status,
		'error' : error,
	}

def update_quantity_prestashop(prestashop, ecomm_id,ecomm_combination_id, quantity):
	try:
		stock_search = prestashop.get('stock_availables', options={'filter[id_product]':ecomm_id, 'filter[id_product_attribute]':ecomm_combination_id})
	except:
		return [0,' Unable to search given stock id']
	if type(stock_search['stock_availables']) == dict:
		stock_id = stock_search['stock_availables']['stock_available']['attrs']['id']
		try:
			stock_data = prestashop.get('stock_availables', stock_id)
		except:
			return [0, ' Error in Updating Quantity,can`t get stock_available data.']
		stock_data['stock_available']['quantity'] = int(quantity)
		try:
			up=prestashop.edit('stock_availables', stock_id, stock_data)
		except:
			return [0, ' Error in Updating Quantity,Not able to get stock.']
		return [1, '']
	return [0, ' Error in Updating Quantity,Not able to get stock.']

def create_images(prestashop, name, image_path, object_name, resource_id, image_name=None, resource='images/products'):
	if image_name == None:
		image_name = 'op' + str(resource_id) + '.png'
	try:
		file_doc = frappe.get_doc("File",{
				"file_url": image_path,
				"attached_to_doctype": object_name,
				"attached_to_name": name
		})
		if file_doc:
			image_data = base64.b64encode(file_doc.get_content())
			returnid = prestashop.add(str(resource) + '/' + str(resource_id), image_data, image_name)
			return returnid
	except Exception as e:
		print("=========error while creating images=============",str(e))
		return False
