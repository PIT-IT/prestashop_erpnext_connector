# -*- coding: utf-8 -*-
# Copyright(c) 2010-present, Webkul Software Pvt Ltd
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import erpnext
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice, make_delivery_note
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request, make_payment_entry
from frappe import _
import json
from frappe.utils.file_manager import save_file

@frappe.whitelist()
def create_pricelist():
	try:
		vals = json.loads(frappe.request.data)
		name = vals.get('name')
		iso_code = vals.get('iso_code')
		return_vals = {'status':False}
		if iso_code:
			check_currency = frappe.db.sql("""
					select `name` from `tabCurrency` where  UPPER(currency_name)="%s" limit 1"""%iso_code.upper())
			if check_currency:
				currency = check_currency[0][0]
				pricelist = frappe.new_doc("Price List").update({'currency':currency,'price_list_name':name,'enabled':1,'selling':1}).insert()
				return_vals.update({
					'name':pricelist.name,
					'status':True
				})
		return return_vals
	except Exception as e:
		print("=========issue while creating pricelist=========%r",str(e))
		raise

@frappe.whitelist()
def create_carrier():
	try:
		vals = json.loads(frappe.request.data)
		return_vals = {'status':False}
		check_carrier = frappe.db.sql("""
				select `name` from `tabShipping Rule` where  UPPER(label)="%s" limit 1"""%vals['label'].upper())
		if check_carrier:
			carrier = check_carrier[0][0]
			return_vals.update({
				'name':carrier,
				'status':True
			})
		else:
			instance = frappe.db.sql("""
					select `shipping_account`,`cost_center`
					from `tabInstance` limit 1""")
			if instance:
				vals.update({
					'account':instance[0][0],
					'cost_center':instance[0][1]
				})
				carrier = frappe.new_doc("Shipping Rule").update(vals).insert()
				return_vals.update({
				'name':carrier.name,
				'status':True
			})
		return return_vals
	except Exception as e:
		print("=========issue while creating carrier=========%r",str(e))
		raise


@frappe.whitelist()
def create_product():
	try:
		instance = update_active_status_instance()
		vals = json.loads(frappe.request.data)
		return_vals = {'status':False}
		check_product = frappe.db.sql("""
				select `name` from `tabItem` where  UPPER(item_name)="%s" limit 1"""%vals['item_name'])
		if check_product:
			product = check_product[0][0]
			return_vals.update({
				'name':product,
				'status':True
			})
		else:
			image = vals.pop('image',False)
			product = frappe.new_doc("Item").update(vals).insert()
			if image:
				create_image(product.name,image)
			return_vals.update({
			'name':product.name,
			'status':True
			})
		return return_vals
	except Exception as e:
		print("=========issue while creating product=========%r",str(e))
		raise
	finally:
		update_active_status_instance(instance)



@frappe.whitelist()
def update_product():
	try:
		instance = update_active_status_instance()
		vals = json.loads(frappe.request.data)
		return_vals = {'status':False}
		erpnext_id = vals.pop('erpnext_id',False)
		product = frappe.get_doc('Item',erpnext_id)
		if vals.get('barcodes'):
			for check_barcode in product.barcodes:
				if check_barcode.name==vals['barcodes'][0]['barcode']:
					vals.pop('barcodes')
		image = vals.pop('image',False)
		product.update(vals).save()
		if image:
			create_image(product.name,image)
		return_vals.update({
		'name':product.name,
		'status':True
		})
		return return_vals
	except Exception as e:
		print("=========issue while updating product=========%r",str(e))
		raise
	finally:
		update_active_status_instance(instance)


def create_image(item,image):
	try:
		item_obj = frappe.get_doc('Item',item)
		if item_obj.image:
			file_doc = frappe.get_doc("File", {
				"file_url": item_obj.image,
				"attached_to_doctype": "Item",
				"attached_to_name": item
			})
			file_doc.delete()
		file_save = save_file(item_obj.item_name+'.png', image, "Item",
					item, folder=None, decode=True, is_private=0, df=True)
		if file_save:
			item_vals = {
			'image':file_save.file_url,
			'website_image':file_save.file_url
			}
			item_obj.update(item_vals).save()
		return True
	except Exception as e:
		print("============ issue creating image ======= %r",str(e))
	

@frappe.whitelist()
def create_attribute():
	try:
		vals = json.loads(frappe.request.data)
		return_vals = {'status':False}
		check_attribute = frappe.db.sql("""
				select `name` from `tabItem Attribute` where  UPPER(attribute_name)="%s" limit 1"""%vals['attribute_name'])
		if check_attribute:
			attribute = check_attribute[0][0]
			return_vals.update({
				'name':attribute,
				'status':True
			})
		else:
			attribute = frappe.new_doc("Item Attribute").update(vals).insert()
			return_vals.update({
			'name':attribute.name,
			'status':True
			})
		return return_vals
	except Exception as e:
		print("=========issue while creating attribute=========%r",str(e))
		raise

@frappe.whitelist()
def create_attribute_value():
	try:
		vals = json.loads(frappe.request.data)
		return_vals = {'status':False}
		check_attribute_value = frappe.db.sql("""
				select `name` from `tabItem Attribute Value` where  UPPER(attribute_value)="%s" limit 1"""%vals['attribute_value'])
		if check_attribute_value:
			attributevalue = check_attribute_value[0][0]
			return_vals.update({
				'name':attributevalue,
				'status':True
			})
		else:
			attributevalue = frappe.new_doc("Item Attribute Value").update(vals).insert()
			return_vals.update({
			'name':attributevalue.name,
			'status':True
			})
		return return_vals
	except Exception as e:
		print("=========issue while creating attribute value=========%r",str(e))
		raise


@frappe.whitelist()
def create_category():
	try:
		vals = json.loads(frappe.request.data)
		vals['item_group_name'] = _unescape(vals['item_group_name'])
		return_vals = {'status':False}
		check_category = frappe.db.sql("""
				select `name` from `tabItem Group` where  UPPER(item_group_name)="%s" limit 1"""%vals['item_group_name'])
		if check_category:
			category = check_category[0][0]
			return_vals.update({
				'name':category,
				'status':True
			})
		else:
			category = frappe.new_doc("Item Group").update(vals).insert()
			return_vals.update({
			'name':category.name,
			'status':True
			})
		return return_vals
	except Exception as e:
		print("=========issue while creating category=========%r",str(e))
		raise

def _unescape(text):
	try:
		from urllib.parse import unquote_plus
		text = unquote_plus(text)
		return text
	except Exception as e:
		print("=========issue while category name escape =========%r",str(e))
		return text

@frappe.whitelist()
def create_payment():
	try:
		vals = json.loads(frappe.request.data)
		return_vals = {'status':False}
		check_payment = frappe.db.sql("""
				select `name` from `tabMode of Payment` where  UPPER(mode_of_payment)="%s" limit 1"""%vals['mode_of_payment'].upper())
		if check_payment:
			payment = check_payment[0][0]
			return_vals.update({
				'name':payment,
				'status':True
			})
		else:
			payment = frappe.new_doc("Mode of Payment").update(vals).insert()
			return_vals.update({
			'name':payment.name,
			'status':True
			})
		return return_vals
	except Exception as e:
		print("=========issue while creating payment=========%r",str(e))
		raise


@frappe.whitelist()
def create_tax():
	try:
		vals = json.loads(frappe.request.data)
		return_vals = {'status':False}
		check_tax = frappe.db.sql("""
				select `name` from `tabItem Tax Template` where  UPPER(title)="%s" limit 1"""%vals['title'].upper())
		if check_tax:
			tax = check_tax[0][0]
			return_vals.update({
				'name':tax,
				'status':True
			})
		else:
			title = vals.get('title')
			rate = vals.get('rate')
			instance = frappe.db.sql("""
					select `tax_account`
					from `tabInstance` limit 1""")
			if instance:
				tax_account = instance[0][0]
				values = {
					'title':title,
					'taxes':[{
						'tax_type':tax_account,
						'tax_rate':float(rate),
						'parentfield':'taxes',
						'parenttype':'Item Tax Template',
						'docstatus':0
					}]
				}
				tax = frappe.new_doc("Item Tax Template").update(values).insert()
				return_vals.update({
				'name':tax.name,
				'status':True
				})
		return return_vals
	except Exception as e:
		print("=========issue while creating tax=========%r",str(e))
		raise


@frappe.whitelist()
def confirm_order():
	try:
		vals = json.loads(frappe.request.data)
		return_vals = {'status':False}
		order_id = vals.get('erpnextorder')
		if order_id:
			orderobj = frappe.get_doc('Sales Order', order_id)
			if orderobj.status=='Draft':
				orderobj.submit()
				return_vals.update({'status':True,'order_id':order_id})
		return return_vals
	except Exception as e:
		print("=========issue while confirming order=========%r",str(e))
		raise


@frappe.whitelist()
def create_invoice(order_id=False):
	try:
		vals = json.loads(frappe.request.data)
		return_vals = {'status':False}
		if not order_id:
			order_id = vals.get('erpnextorder')
		if order_id:
			orderobj = frappe.get_doc('Sales Order', order_id)
			if orderobj.status=='Draft':
				orderobj.submit()
			check_invoice = frappe.db.sql("""
				select `parent` from `tabSales Invoice Item` where  sales_order="%s" limit 1"""%order_id)
			if not check_invoice:
				getsaledoc = make_sales_invoice(order_id)
				getsaledoc.save()
				getsaledoc.submit()
				sale_doc = getsaledoc.name
			else:
				sale_doc = check_invoice[0][1]
			return_vals.update({'status':True,'invoice':sale_doc})
		return return_vals
	except Exception as e:
		print("=========issue while creating invoice=========%r",str(e))
		raise


def check_invoice(order_id=False):
	return_vals = {'status':False}
	if order_id:
		orderobj = frappe.get_doc('Sales Order', order_id)
		if orderobj.status=='Draft':
			orderobj.submit()
		check_invoice = frappe.db.sql("""
			select `parent` from `tabSales Invoice Item` where  sales_order="%s" limit 1"""%order_id)
		if not check_invoice:
			getsaledoc = make_sales_invoice(order_id)
			getsaledoc.save()
			getsaledoc.submit()
			sale_doc = getsaledoc.name
		else:
			sale_doc = check_invoice[0][0]
		return_vals.update({'status':True,'invoice_id':sale_doc})
	return return_vals

@frappe.whitelist()
def cancel_order():
	try:
		instance = update_active_status_instance()
		vals = json.loads(frappe.request.data)
		order_id = vals.get('erpnextorder')
		status = False
		if order_id:
			check_invoice = frappe.db.sql("""
				select `parent` from `tabSales Invoice Item` where  sales_order="%s" limit 1"""%order_id)
			if check_invoice:
				invoice_doc = check_invoice[0][0]
				invoiceObj = frappe.get_doc("Sales Invoice", invoice_doc)
				invoiceObj.cancel()
			frappe.get_doc('Sales Order', order_id).cancel()
			status = True
		return {'status':status}
	except Exception as e:
		print("=========issue while cancelling order=========%r",str(e))
		raise
	finally:
		update_active_status_instance(instance)


def update_active_status_instance(instance=False):
	print("========istance========%r",instance)
	if instance:
		frappe.db.sql("""update `tabInstance`
					set active =1 where name='%s'"""%instance)
	else:
		instance_data = frappe.db.sql("""
				select `name`
				from `tabInstance` WHERE `active`=1""")
		if instance_data:
			instance = instance_data[0][0]
			frappe.db.sql("""update `tabInstance`
					set active =0 where name='%s'"""%instance)
	return instance

@frappe.whitelist()
def set_order_paid():
	try:
		instance = update_active_status_instance()
		vals = json.loads(frappe.request.data)
		return_vals = {'status':False}
		order_id = vals.get('erpnextorder')
		mod_of_payment = vals.get('mode_of_payment')
		if order_id and mod_of_payment:
			getinvoice = check_invoice(order_id)
			if getinvoice['status']:
				invoice_id = getinvoice['invoice_id']
				invoiceObj = frappe.get_doc("Sales Invoice", invoice_id)
				payment_dict = make_payment_request(dt="Sales Invoice", dn=invoiceObj.name, recipient_id=invoiceObj.contact_email,mute_email=True)
				payment_dict['mode_of_payment'] = mod_of_payment
				payment_request = frappe.new_doc('Payment Request').update(payment_dict).insert()
				payment_request.submit()
				payment_entry = frappe.get_doc(make_payment_entry(payment_request.name))
				payment_entry.posting_date = frappe.flags.current_date
				payment_entry.submit()
				return_vals.update({'status':True,'invoice':getinvoice})
		return return_vals
	except Exception as e:
		print("=========issue while paying order=========%r",str(e))
		raise
	finally:
		update_active_status_instance(instance)

@frappe.whitelist()
def set_order_shipped():
	try:
		instance = update_active_status_instance()
		vals = json.loads(frappe.request.data)
		status = False
		order_id = vals.get('erpnextorder')
		if order_id:
			check_delivery = frappe.db.sql("""
				select `parent` from `tabDelivery Note Item` where  against_sales_order="%s" limit 1"""%order_id)
			if check_delivery:
				delivery_note = frappe.get_doc('Delivery Note',check_delivery[0][0])
				if delivery_note.status=='Draft':
					delivery_note.submit()
				delivery_name = delivery_note.name
				status = True
			else:
				orderobj = frappe.get_doc('Sales Order', order_id)
				if orderobj.status=='Draft':
					orderobj.submit()
				delivery_note = make_delivery_note(order_id)
				delivery_note.save()
				delivery_note.submit()
				delivery_name = delivery_note.name
				status = True
		return {"status":status,'delivery_id':delivery_name}
	except Exception as e:
		print("=========issue while delivering order=========%r",str(e))
		raise
	finally:
		update_active_status_instance(instance)



@frappe.whitelist()
def create_order():
	try:
		vals = json.loads(frappe.request.data)
		return_vals = {'status':False}
		instance = frappe.db.sql("""
				select `tax_account`,`warehouse`,`coupon_product`,`shipping_product`
				from `tabInstance` limit 1""")
		ecommerce_order_id = vals.pop('ecommerce_order_id')
		if instance:
			warehouse = instance[0][1]
			coupon_product = instance[0][2]
			shipping_product = instance[0][3]
			vals = get_default_fields(vals, warehouse, shipping_product, coupon_product)
			order = frappe.new_doc("Sales Order").update(vals).insert()
			if order:
				frappe.new_doc("OrderMapping").update({'title':order.name,'erpnext_id':order.name,'ecomm_id': ecommerce_order_id,'created_by':'prestashop'}).insert()
				return_vals = {
					'status':True,
					'name':order.name
				}
		return return_vals
	except Exception as e:
		print("=========issue while creating order=========%r",str(e))
		raise

def get_default_fields(vals, warehouse, shipping_product, coupon_product):
	pricelist_id = vals.get('selling_price_list')
	if pricelist_id:
		pricelistObj = frappe.get_doc("Price List", pricelist_id)
		vals.update(dict(
			currency=pricelistObj.currency,
		))
	customer = vals.get('customer')
	if customer:
		customerObj = frappe.get_doc("Customer", customer)
		vals['contact_person'] = customerObj.customer_primary_contact
	vals['set_warehouse'] = warehouse
	vals['taxes'] = []
	for item in vals['items']:
		item_type = item.pop('type',False)
		taxes = item.pop('taxes',False)
		tax_amount = item.pop('tax_amount',0.0)
		if item_type=='item':
			dic_tax = {}
			if taxes:
				item['Item Tax Template'] = taxes[0]
				ItemTaxTemplate = frappe.get_doc('Item Tax Template',taxes[0])
				dic_tax = {ItemTaxTemplate.taxes[0].tax_type:ItemTaxTemplate.taxes[0].tax_rate}
				tax_vals = {
					'charge_type':'Actual',
					'account_head':ItemTaxTemplate.taxes[0].tax_type,
					'description':ItemTaxTemplate.title,
					'parenttype':'Sales Order',
					'tax_amount':tax_amount
				}
				vals['taxes'].append(tax_vals)
			if dic_tax:
				item['item_tax_rate'] = json.dumps(dic_tax)
		if item_type=='shipping':
			itemObj = frappe.get_doc("Item", shipping_product)
			item.update(dict(
				item_code = itemObj.name,
			))
			if taxes:
				ItemTaxTemplate = frappe.get_doc('Item Tax Template',taxes[0])
				item['Item Tax Template'] = taxes[0]
				item['item_tax_rate'] = json.dumps({ItemTaxTemplate.taxes[0].tax_type:ItemTaxTemplate.taxes[0].tax_rate})
				tax_vals = {
					'charge_type':'Actual',
					'account_head':ItemTaxTemplate.taxes[0].tax_type,
					'description':ItemTaxTemplate.title,
					'parenttype':'Sales Order',
					'tax_amount':tax_amount
				}
				vals['taxes'].append(tax_vals)
	return vals



