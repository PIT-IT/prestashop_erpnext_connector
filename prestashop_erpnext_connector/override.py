# -*- coding: utf-8 -*-
# Copyright(c) 2010-present, Webkul Software Pvt Ltd
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import erpnext
import prestashop_erpnext_connector
from prestashop_erpnext_connector.prestapi.prestapi import PrestaShopWebService,PrestaShopWebServiceDict,PrestaShopWebServiceError,PrestaShopAuthenticationError
from erpnext.stock.utils import get_stock_balance
from frappe.utils import flt, cstr, nowdate, nowtime


def on_update(obj, method):
	check_active_id = frappe.db.sql("""
				select `api_url`,`api_key`
				from `tabInstance` where active=1 limit 1""")
	if check_active_id and check_active_id[0]:
		frappe.db.sql("""update `tabProductVariantMapping`
					set is_sync =0 where erpnext_variant_id='%s'"""%obj.name)
		mapping = frappe.db.sql("""
				select `erpnext_id`
				from `tabProductVariantMapping` WHERE `erpnext_variant_id`='%s'"""%obj.name)
		if mapping:
			frappe.db.sql("""update `tabProductMapping`
					set is_sync =0 where erpnext_id='%s'"""%mapping[0][0])

def on_payment_submit(obj, method):
	if obj and obj.references:
		if obj.references[0].reference_doctype=='Sales Invoice':
			get_order = frappe.db.sql("""
			select `sales_order` from `tabSales Invoice Item` where  parent="%s" limit 1"""%obj.references[0].reference_name)
			if get_order and get_order[0]:
				sale_order = get_order[0][0]
				update_order_status(sale_order, 2, 'invoice_status')
	

def on_delivery_submit(obj, method):
	if obj and obj.items:
		sale_order = obj.items[0].against_sales_order
		if sale_order:
			update_order_status(sale_order, 4, 'shipping_status')

def on_sale_cancel(obj, method):
	sale_order = obj.name
	if sale_order:
		update_order_status(sale_order, 6, 'cancel_status')
		 
def update_order_status(ordername, ps_status, fieldname):
	check_active_id = frappe.db.sql("""
				select `api_url`,`api_key`,`%s`
				from `tabInstance` where active=1 limit 1"""%fieldname)
	if check_active_id:
		url = check_active_id[0][0]
		key = check_active_id[0][1]
		status = check_active_id[0][2]
		if status:
			check_mapping = frappe.db.sql("""
				select `ecomm_id`
				from `tabOrderMapping` where `erpnext_id`='%s'"""%ordername)
			if check_mapping:
				ps_order = check_mapping[0][0]
				prestashop = PrestaShopWebServiceDict(url,key)
				update_order_status_prestashop(prestashop, ps_order, ps_status)


def update_order_status_prestashop(prestashop, id_order, id_order_state):
	try:
		order_his_data = prestashop.get('order_histories', options={'schema': 'blank'})
		order_his_data['order_history'].update({
		'id_order' : id_order,
		'id_order_state' : id_order_state
		})
		endpoint = 'order_histories?sendemail=1&from_erpnext=1'
		state_update = prestashop.add(endpoint, order_his_data)
		status = 'yes'
	except Exception as e:
		text = 'Status Not Updated For Order Id '+ str(id_order) + ' And Error is ' + str(e)
		print(text)
	return True


def on_stock_update(obj, method):
	if obj.flags.via_stock_ledger_entry:
		check_active_id = frappe.db.sql("""
					select `api_url`,`api_key`,`stock_update`,`warehouse`
					from `tabInstance` where active=1 limit 1""")
		if check_active_id:
			url = check_active_id[0][0]
			key = check_active_id[0][1]
			stock_update = check_active_id[0][2]
			warehouse = check_active_id[0][3]
			check_mapping = frappe.db.sql("""
					select `ecomm_id`,`ecomm_variant_id`
					from `tabProductVariantMapping` where `erpnext_variant_id`='%s'"""%obj.item_code)
			if check_mapping and obj.warehouse==warehouse and stock_update:
				ecomm_id = check_mapping[0][0]
				ecomm_combination_id = check_mapping[0][1]
				quantity = obj.actual_qty or 0.0
				quantity_update_to_prestashop(url, key, ecomm_id, ecomm_combination_id, quantity)

def quantity_update_to_prestashop(api_url, api_key,ecomm_id, ecomm_combination_id, quantity):
	prestashop = PrestaShopWebServiceDict(api_url, api_key)
	try:
		stock_search = prestashop.get('stock_availables',
										options={'filter[id_product]':ecomm_id,
										'filter[id_product_attribute]':ecomm_combination_id})
	except Exception as e:
		print("===========Error While Fetching Stock Available for ecomm id%s,comb id%s, wiht error%s",(ecomm_id,ecomm_combination_id,str(e)))
		pass
	if type(stock_search['stock_availables']) == dict:
		if isinstance(stock_search['stock_availables']['stock_available'],list):
			stock_id = stock_search['stock_availables']['stock_available'][0]['attrs']['id']
		else:
			stock_id = stock_search['stock_availables']['stock_available']['attrs']['id']
		try:
			stock_data = prestashop.get('stock_availables', stock_id)
		except Exception as e:
			print("===========Error While Fetching Stock Available for stock id:%s, with error%s",(stock_id,str(e)))
			pass
		stock_data['stock_available']['quantity'] = int(quantity)
		try:
			up = prestashop.edit('stock_availables', stock_id, stock_data)
		except Exception as e:
			print("===========Error While Fetching Stock Available for stock id:%s, with error%s",(stock_id,str(e)))
