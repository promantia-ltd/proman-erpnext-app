frappe.ui.form.on('Delivery Trip', {
	refresh(frm) {
		frm.set_query("address", "delivery_stops_supplier", function (doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			if (row.supplier) {
				return {
					query: 'frappe.contacts.doctype.address.address.address_query',
					filters: {
						link_doctype: "Supplier",
						link_name: row.supplier
					}
				};
			}
			
		})
		
		if (frm.doc.docstatus === 0) {
		frm.add_custom_button(__('Stock Entry'), function(){
			var select={}
			frm.set_value("type","Supplier")
			refresh_field("type")
			let dialogObj= new frappe.ui.form.MultiSelectDialog({
 			doctype: "Stock Entry",
 			target: frm,
 			setters: {
 				company: frm.doc.company,
 			},
			 
 			date_field: "posting_date",
 			get_query() {
 				return {
 					filters: {  
						docstatus: 1,
						company: frm.doc.company,
						stock_entry_type:"Send to Subcontractor"
					}
 				}
 			},
 			action(selections) {
				var count=0
				select=selections
 				$.each(selections,function(idx){
					console.log(select[idx])
					 count=0
				    $.each(frm.doc.delivery_stops_supplier, function(id, detail){
				        if(detail.stock_entry==select[idx]){
						console.log(detail.stock_entry,select[idx])
				            count=1;
				        }
				    })
					if(count==0){
						var suppliername="";
						var child = cur_frm.add_child("delivery_stops_supplier");
						child.stock_entry=select[idx]
						frappe.db.get_value("Stock Entry",select[idx],"purchase_order",(c)=>{
							frappe.db.get_value("Purchase Order",c.purchase_order,["supplier","supplier_address","address_display"],(p)=>{
							child.supplier=p.supplier
							child.address=p.supplier_address
							child.supplier_address=p.address_display
							suppliername=p.supplier
							refresh_field("delivery_stops_supplier")
						})
					})
				}
			})
				dialogObj.dialog.hide()
			}
			})
			}, __("Get suppliers from"));
		}
	},
	current_reading:function(frm,cdt,cdn){
		frm.set_value('distance',(frm.doc.current_reading-frm.doc.previous_reading)*frm.doc.unit_rate)
	},
	previous_reading:function(frm,cdt,cdn){
		frm.set_value('distance',(frm.doc.current_reading-frm.doc.previous_reading)*frm.doc.unit_rate)
	},
	unit_rate:function(frm,cdt,cdn){
		frm.set_value('distance',(frm.doc.current_reading-frm.doc.previous_reading)*frm.doc.unit_rate)
	}
})

frappe.ui.form.on('Delivery Stops Supplier', {
	address: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.address) {
			frappe.call({
				method: "frappe.contacts.doctype.address.address.get_address_display",
				args: { "address_dict": row.address },
				callback: function (r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, "supplier_address", r.message);
					}
				}
			});
		} else {
			frappe.model.set_value(cdt, cdn, "supplier_address", "");
		}
		refresh_field("delivery_stops_supplier")
	},
	supplier: function (frm, cdt, cdn) {
		frappe.model.set_value(cdt, cdn, "address", "");
		frappe.model.set_value(cdt, cdn, "supplier_address", "");
		frappe.model.set_value(cdt, cdn, "stock_entry", "");
	},
	departure_time:function(frm, cdt, cdn){
		type_delivery_note(frm,cdt,cdn);
 	}
})
function type_delivery_note(frm,cdt,cdn){
	var d = locals[cdt][cdn];
	frm.doc.delivery_stops.forEach(function(d) {
		if(d.delivery_note != undefined){
			frm.set_value("type","Customer")	
			refresh_field("type")
		}
	})
}