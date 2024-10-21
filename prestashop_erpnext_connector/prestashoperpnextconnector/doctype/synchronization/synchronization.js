// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Synchronization', {
	refresh: function(frm) {

	}
});
frappe.ui.form.on("Synchronization", "export_attributes", function(frm) {
	frappe.call({
	  method: "prestashop_erpnext_connector.prestashoperpnextconnector.doctype.synchronization.attribute.export_attributes",
	  callback: function (data) {
        console.log(data);                
    }
	});
  });
  frappe.ui.form.on("Synchronization", "export_categories", function(frm) {
	frappe.call({
	  method: "prestashop_erpnext_connector.prestashoperpnextconnector.doctype.synchronization.category.export_categories",
	  callback: function (data) {
        console.log(data);                
    }
	});
  });
  frappe.ui.form.on("Synchronization", "export_attribute_values", function(frm) {
	frappe.call({
	  method: "prestashop_erpnext_connector.prestashoperpnextconnector.doctype.synchronization.attributevalue.export_attributevalues",
	  callback: function (data) {
        console.log(data);                
    }
	});
  });

  frappe.ui.form.on("Synchronization", "export_products", function(frm) {
	frappe.call({
	  method: "prestashop_erpnext_connector.prestashoperpnextconnector.doctype.synchronization.product.export_products",
	  callback: function (data) {
        console.log(data);                
    }
	});
  });

  frappe.ui.form.on("Synchronization", "update_products", function(frm) {
	frappe.call({
	  method: "prestashop_erpnext_connector.prestashoperpnextconnector.doctype.synchronization.product.update_products",
	  callback: function (data) {
        console.log(data);                
    }
	});
  });

