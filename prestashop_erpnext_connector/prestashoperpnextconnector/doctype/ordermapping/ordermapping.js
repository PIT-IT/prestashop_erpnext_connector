// Copyright (c) 2010-present, Webkul Software Pvt Ltd
// For license information, please see license.txt

frappe.ui.form.on('OrderMapping', {
	refresh: function(frm) {
		frappe.breadcrumbs.clear();

	    frappe.breadcrumbs.set_custom_breadcrumbs({
                label: 'PrestashopConnector',
                route: '/app/prestashopconnector',
            });

	    frappe.breadcrumbs.set_custom_breadcrumbs({
                label: 'OrderMappings',
                route: '/app/ordermapping',
            });

	    frappe.breadcrumbs.set_custom_breadcrumbs({
                label: frm.doc.name,
                route: '/app/ordermapping/'+frm.doc.name,
            });
	}
});
