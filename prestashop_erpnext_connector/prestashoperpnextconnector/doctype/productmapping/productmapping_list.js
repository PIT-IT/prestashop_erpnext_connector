// Copyright (c) 2010-present, Webkul Software Pvt Ltd
// For license information, please see license.txt

frappe.listview_settings['ProductMapping'] = { 
        before_render() {
            frappe.breadcrumbs.clear();

            frappe.breadcrumbs.set_custom_breadcrumbs({
                label: 'PrestashopConnector',
                route: '/app/prestashopconnector',
            });

            frappe.breadcrumbs.set_custom_breadcrumbs({
                label: 'ProductMappings',
                route: '/app/productmapping',
            });
        }
}
