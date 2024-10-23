// Copyright (c) 2010-present, Webkul Software Pvt Ltd
// For license information, please see license.txt

frappe.ui.form.on('Instance', {
	refresh: function(frm) {

	    frappe.breadcrumbs.clear();

	    frappe.breadcrumbs.set_custom_breadcrumbs({
                label: 'PrestashopConnector',
                route: '/app/prestashopconnector',
            });

	    frappe.breadcrumbs.set_custom_breadcrumbs({
                label: 'ConnectorInstance',
                route: '/app/instance',
            });

	    frappe.breadcrumbs.set_custom_breadcrumbs({
                label: frm.doc.name,
                route: '/app/instance/'+frm.doc.name,
            });

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

