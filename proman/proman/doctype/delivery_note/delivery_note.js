frappe.ui.form.on('Delivery Note', {
	refresh(frm) {
		frm.page.remove_menu_item(__('Send SMS'), function() {  });
	}
})
