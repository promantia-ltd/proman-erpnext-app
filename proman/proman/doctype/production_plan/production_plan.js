frappe.ui.form.on('Production Plan', {
	setup: function(frm) {
		frm.custom_make_buttons = {
			'Work Order': 'Work Order',
			'Material Request': 'Material Request',
			'Service Request': 'Service Request'
		};
	},
	refresh: function(frm) {
		if (frm.doc.status !== "Completed") {
			if (frm.doc.po_items && frm.doc.status !== "Closed" && frm.doc.docstatus==1) {
				frm.add_custom_button(__("Service Request"), ()=> {
					frm.trigger("make_service_request");
				}, __('Create'));
			}
		}
	},
	make_service_request: function(frm){
	frappe.call({
		method: 'proman.proman.doctype.production_plan.production_plan.auto_create_service_request',
		args: {
		doc: frm.doc
		},
		callback: function(r) {
		if(r.message) {
			frappe.msgprint("inserted");
		} 
		}
		})
	}
});
