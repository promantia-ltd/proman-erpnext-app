frappe.ui.form.on('Project', {
	onload(frm) {
		var gm = frm.doc.total_billed_amount - frm.doc.total_billable_amount - frm.doc.total_expense_claim - frm.doc.total_consumed_material_cost
        if ( frm.doc.gross_margin_amount != gm.toFixed(2) ){
            frm.set_value("gross_margin_amount", gm);
            refresh_field("gross_margin_amount");
            cur_frm.save();
        }
	}
})