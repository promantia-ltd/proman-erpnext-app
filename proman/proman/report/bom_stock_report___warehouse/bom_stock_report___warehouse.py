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
		_("Enough Parts to Build") + ":Int:200",
		_("Shortage") + ":Int:200",
		_("Warehouse")+":Link/Warehouse:150",
	]

	return columns

def get_bom_stock(filters):
	records=[]
	bom_list=[]
	conditions = ""
	bom = filters.get("bom")
	qty=frappe.db.get_value('BOM',{'name':bom},'quantity')
	qty_field = "stock_qty"
	
	qty_to_produce = filters.get("qty_to_produce", 1)
	if  int(qty_to_produce) <= 0:
		frappe.throw(_("Quantity to Produce can not be less than Zero"))

	query="""
			select bom.item,
			bom.description ,
			bom.bom_qty ,
			bom.bom_uom,
			bom.required_qty,
			ledger.actual_qty as in_stock_qty,
			(FLOOR(ledger.actual_qty/bom.bom_qty)) as enough_parts_to_build,
			(FLOOR(CASE WHEN (CASE WHEN bom.required_qty > ledger.actual_qty THEN 0 ELSE (ledger.actual_qty/bom.bom_qty) END) < {qty_to_produce} THEN (bom.required_qty - (CASE WHEN bom.required_qty > ledger.actual_qty THEN 0 ELSE (ledger.actual_qty/bom.bom_qty) END) - ledger.actual_qty) ELSE 0 END)) as shortage,
			(FLOOR(ledger.actual_qty / (bom.bom_qty * {qty_to_produce}/ {qty}))) as enough_parts_to_builds,
			ledger.warehouse
			from `tabBin` AS ledger 
			INNER JOIN (SELECT 
			item,
			description,
			bom_qty,
			bom_uom,
			required_qty

			from (WITH RECURSIVE item_hierarchy AS (
			SELECT    
			t.item_code as item,
			t.bom_no,
			t.description ,
			t.stock_qty as bom_qty,
			t.stock_uom as bom_uom,
			t.{qty_field} * {qty_to_produce}/ {qty} as required_qty
			FROM
			`tabBOM Item` t
			where t.parent={bom}

			UNION ALL

			SELECT
			e.item_code as item,
			e.bom_no,
			e.description ,
			e.stock_qty as bom_qty,
			e.stock_uom as bom_uom,
			e.{qty_field} * {qty_to_produce}/ {qty} as required_qty
			FROM  item_hierarchy,`tabBOM Item` e
			WHERE e.parent = item_hierarchy.bom_no
			)
			SELECT *
			FROM item_hierarchy ) as t1)as bom
			ON bom.item = ledger.item_code where ledger.actual_qty>0 or ledger.warehouse='Bidadi Stores - PISPL'
		 """.format(
				qty_field=qty_field,
				conditions=conditions,
				bom=frappe.db.escape(bom),
				qty=qty,
				qty_to_produce=qty_to_produce or 1)

	bom_item_list= frappe.db.sql(query, as_dict=True)
	for item in bom_item_list:
		records.append(item)
		if item.bom_no:
			bom_list.append(item.bom_no)
	
	if len(bom_list)>1:
		condition=f"""SELECT
			explod_item.item_code as item,
			explod_item.description,
			explod_item.stock_qty as bom_qty,
			explod_item.stock_uom  as bom_uom,
			explod_item.stock_qty * {qty_to_produce or 1}/ {qty} as required_qty,
			ledger.actual_qty as in_stock_qty,
			(FLOOR(ledger.actual_qty/explod_item.stock_qty)) as enough_parts_to_build,
			(FLOOR (CASE WHEN ( CASE WHEN (explod_item.stock_qty * {qty_to_produce or 1}/ {qty}) > ledger.actual_qty THEN 0 ELSE (ledger.actual_qty/explod_item.stock_qty) END) < {qty_to_produce} THEN (explod_item.stock_qty * {qty_to_produce or 1}/ {qty}) - ( CASE WHEN (explod_item.stock_qty * {qty_to_produce or 1}/ {qty}) > ledger.actual_qty THEN 0 ELSE (ledger.actual_qty/explod_item.stock_qty) END) - ledger.actual_qty ELSE 0 END))as shortage,
			(FLOOR(ledger.actual_qty / (explod_item.stock_qty * {qty_to_produce}/ {qty})))  as enough_parts_to_builds,
			ledger.warehouse
		FROM
			`tabBOM Explosion Item` AS explod_item 
		LEFT JOIN `tabBin` AS ledger
				ON explod_item.item_code = ledger.item_code WHERE
			explod_item.parent in {frappe.db.escape(tuple(bom_list))} or explod_item.parent={filters.get("bom")}
			and ledger.actual_qty > 0 or ledger.warehouse='Bidadi Stores - PISPL' """
	else:
		condition=f"""SELECT
			explod_item.item_code as item,
			explod_item.description,
			explod_item.stock_qty as bom_qty,
			explod_item.stock_uom  as bom_uom,
			explod_item.stock_qty * {qty_to_produce or 1}/ {qty} as required_qty,
			ledger.actual_qty as in_stock_qty,
			(FLOOR( ledger.actual_qty/explod_item.stock_qty) as enough_parts_to_build,
			(FLOOR (CASE WHEN ( CASE WHEN (explod_item.stock_qty * {qty_to_produce or 1}/ {qty}) > ledger.actual_qty THEN 0 ELSE (ledger.actual_qty/explod_item.stock_qty) END) < {qty_to_produce} THEN (explod_item.stock_qty * {qty_to_produce or 1}/ {qty}) - ( CASE WHEN (explod_item.stock_qty * {qty_to_produce or 1}/ {qty}) > ledger.actual_qty THEN 0 ELSE (ledger.actual_qty/explod_item.stock_qty) END) - ledger.actual_qty ELSE 0 END))as shortage,
			(FLOOR(ledger.actual_qty / (explod_item.stock_qty * {qty_to_produce}/ {qty})))  as enough_parts_to_builds,
			ledger.warehouse
		FROM
			`tabBOM Explosion Item` AS explod_item 
		LEFT JOIN `tabBin` AS ledger
				ON explod_item.item_code = ledger.item_code WHERE
			explod_item.parent = {frappe.db.escape(tuple(bom_list))} or explod_item.parent={filters.get("bom")}
			and ledger.actual_qty > 0 or ledger.warehouse='Bidadi Stores - PISPL'"""
	
	exploded_item_list= frappe.db.sql(query, as_dict=True)
	for item in exploded_item_list:
		if item not in records and item.in_stock_qty>0 :
			records.append(item)

	return records