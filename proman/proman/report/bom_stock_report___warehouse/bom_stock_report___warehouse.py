# Copyright (c) 2013, proman_app and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()

	data = get_bom_stock(filters)

	return columns, data

def get_columns():
	"""return columns"""
	columns = [
		_("Item") + ":Link/Item:150",
		_("Description") + "::300",
		_("BOM Qty") + ":Float:160",
		_("BOM UoM") + "::160",
		_("Required Qty") + ":Float:120",
		_("In Stock Qty") + ":Float:120",
		_("Enough Parts to Build") + ":Float:200",
		_("Warehouse")+":Link/Warehouse:150",
	]

	return columns

def get_bom_stock(filters):
	records=[]
	data=[]
	conditions = ""
	bom = filters.get("bom")
	qty=frappe.db.get_value('BOM',{'name':bom},'quantity')
	qty_field = "stock_qty"
	
	qty_to_produce = filters.get("qty_to_produce", 1)
	if  int(qty_to_produce) <= 0:
		frappe.throw(_("Quantity to Produce can not be less than Zero"))

	query="""
			(select * from (WITH RECURSIVE item_hierarchy AS (
  			SELECT    
				t.item_code as item,
				t.description ,
				t.stock_qty as bom_qty,
				t.stock_uom as bom_uom,
				t.{qty_field} * {qty_to_produce}/ qty as required_qty,
				ledger.actual_qty as in_stock_qty,
				ledger.actual_qty / (t.{qty_field} * {qty_to_produce}/ qty) as enough_parts_to_build,
				ledger.warehouse,
				t.bom_no
			FROM
				`tabBOM Item` t LEFT JOIN `tabBin` AS ledger
					ON t.item_code = ledger.item_code
		where t.parent={bom} 
		
		UNION ALL
		
		SELECT
			e.item_code as item,
			e.description ,
			e.stock_qty as bom_qty,
			e.stock_uom  as bom_uom,
			e.{qty_field} * {qty_to_produce} / qty as required_qty,
			ledger.actual_qty as in_stock_qty,
			ledger.actual_qty / (e.{qty_field} * {qty_to_produce}/ qty)  as enough_parts_to_build,
			ledger.warehouse,
			e.bom_no

		FROM  item_hierarchy,`tabBOM Item` e  LEFT JOIN `tabBin` AS ledger
							ON e.item_code = ledger.item_code
		WHERE e.parent = item_hierarchy.bom_no 
		)
			SELECT *
			FROM item_hierarchy)as t1)
					""".format(
				qty_field=qty_field,
				conditions=conditions,
				bom=frappe.db.escape(bom),
				qty=qty,
				qty_to_produce=qty_to_produce or 1)

	bom_item_list= frappe.db.sql(query, as_dict=True)
	for item in bom_item_list:
		records.append(item)
	
	for record in records:
		if record.bom_no:
			query="""SELECT
					explod_item.item_code as item,
					explod_item.description,
					explod_item.stock_qty as bom_qty,
					explod_item.stock_uom  as bom_uom,
					explod_item.stock_qty * {qty_to_produce}/ qty as required_qty,
					ledger.actual_qty as in_stock_qty,
					ledger.actual_qty / (explod_item.stock_qty * {qty_to_produce}/ qty)  as enough_parts_to_build,
					ledger.warehouse
				FROM
					`tabBOM Explosion Item` AS explod_item 
				LEFT JOIN `tabBin` AS ledger
						ON explod_item.item_code = ledger.item_code
				WHERE
				explod_item.parent={bom} or explod_item.parent={parent}
				and ledger.actual_qty > 0""".format(
					qty_field=qty_field,
					conditions=conditions,
					bom=frappe.db.escape(record.bom_no),
					parent=frappe.db.escape(bom),
					qty=qty,
					qty_to_produce=qty_to_produce or 1)

			exploded_item_list= frappe.db.sql(query, as_dict=True)
			for item in exploded_item_list:
				if item not in records:
					records.append(item)
		
	for val in records:
		if val.in_stock_qty>0 and val not in data:
			data.append(val)

	return data