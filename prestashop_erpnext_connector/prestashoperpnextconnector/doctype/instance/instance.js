// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Instance', {
	refresh: function(frm) {

	}
});
frappe.ui.form.on("Instance", "test_connection", function(frm) {
	frappe.call({
	  method: "prestashop_erpnext_connector.prestashoperpnextconnector.doctype.instance.instance.test_connection",
	  callback: function (data) {
        console.log(data);                
    }
	});
  });
