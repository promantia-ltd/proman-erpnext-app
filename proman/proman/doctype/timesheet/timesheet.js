// Copyright (c) 2021, proman_app and contributors
// For license information, please see license.txt

frappe.ui.form.on("Timesheet Detail", "no_of_workers",function(frm, doctype, name) {
	set_billing_hours(cur_frm, doctype, name)
});

frappe.ui.form.on("Timesheet Detail", "individual_hours",function(frm, doctype, name) {
	set_billing_hours(cur_frm, doctype, name)
});

frappe.ui.form.on("Timesheet Detail", "is_billable",function(frm, doctype, name) {
	set_billing_hours(cur_frm, doctype, name)
});

function set_billing_hours(cur_frm,doctype,name){
	var row = locals[doctype][name];
	row.hours=row.individual_hours*row.no_of_workers
	if(row.is_billable==1){
		row.billing_hours=row.individual_hours*row.no_of_workers
	}
	cur_frm.refresh_fields('time_logs');
}


