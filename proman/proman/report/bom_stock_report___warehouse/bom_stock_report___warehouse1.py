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
		_("parent") + ":Link/BOM:150",
		_("BOM UoM") + "::160",
		_("Required Qty") + ":Float:120",
		_("In Stock Qty") + ":Float:120",
		_("Enough Parts to Build") + ":Float:200",
		_("Warehouse")+":Link/Warehouse:150",
	]

	return columns

def get_bom_stock(filters):
	records=[]
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
			t.item_code,
         	t.description ,
			t.stock_qty,
			t.parent,
			t.stock_uom,
			t.{qty_field} * {qty_to_produce}/ qty,
			ledger.actual_qty as actual_qty,
			ledger.actual_qty / (t.{qty_field} * {qty_to_produce}/ qty),
			ledger.warehouse,
			t.bom_no
			FROM
				`tabBOM Item` t LEFT JOIN `tabBin` AS ledger
					ON t.item_code = ledger.item_code
		where t.parent={bom} 
		
		UNION ALL
		
		SELECT
		e.item_code,
			e.description ,
			e.stock_qty,
			e.parent,
			e.stock_uom,
			e.{qty_field} * {qty_to_produce} / qty,
			ledger.actual_qty as actual_qty,
			ledger.actual_qty / (e.{qty_field} * {qty_to_produce}/ qty),
			ledger.warehouse,
			e.bom_no

		FROM  item_hierarchy,`tabBOM Item` e  LEFT JOIN `tabBin` AS ledger
							ON e.item_code = ledger.item_code
		WHERE e.parent = item_hierarchy.bom_no 
		)
			SELECT *
			FROM item_hierarchy)as t1 where t1.actual_qty > 0)
					""".format(
				qty_field=qty_field,
				conditions=conditions,
				bom=frappe.db.escape(bom),
				qty=qty,
				qty_to_produce=qty_to_produce or 1)
	bom_list= frappe.db.sql(query, as_list=True)
	for row in bom_list:
		records.append(row)
	
	for record in records:
		if record.bom_no:
			query="""SELECT
					explod_item.item_code,
					explod_item.description,
					explod_item.stock_qty,
					explod_item.parent,
					explod_item.stock_uom,
					explod_item.stock_qty * 1 / qty,
					ledger.actual_qty as actual_qty,
					ledger.actual_qty / (explod_item.stock_qty *1/ qty),
					ledger.warehouse
				FROM
					`tabBOM Explosion Item` AS explod_item 
				LEFT JOIN `tabBin` AS ledger
						ON explod_item.item_code = ledger.item_code
				WHERE
				explod_item.parent="BOM-1301901-002")
				and ledger.actual_qty>0""".format(
					qty_field=qty_field,
					conditions=conditions,
					bom=frappe.db.escape(record.bom_no),
					qty=qty,
					qty_to_produce=qty_to_produce or 1)
			exploded_list= frappe.db.sql(query, as_list=True)
			for row in exploded_list:
				records.append(row)
	
	return records