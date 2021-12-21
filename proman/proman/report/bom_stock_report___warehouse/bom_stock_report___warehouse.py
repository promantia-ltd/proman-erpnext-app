# Copyright (c) 2013, proman_app and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from operator import itemgetter

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()

	data = get_bom_stock(filters)
	data=sorted(data, key=itemgetter('item'))

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
	default_warehouse=frappe.db.get_single_value("Stock Settings","default_warehouse")
	qty_field = "stock_qty"
	
	qty_to_produce = filters.get("qty_to_produce", 1)
	if  int(qty_to_produce) <= 0:
		frappe.throw(_("Quantity to Produce can not be less than Zero"))

	query="""
			select DISTINCT bom.item,
			bom.description ,
			bom.bom_qty ,
			bom.bom_uom,
			bom.required_qty,
			CASE WHEN ledger.warehouse IS NULL or ledger.actual_qty= 0 THEN 0 ELSE ledger.actual_qty END as in_stock_qty,
			CASE WHEN ledger.warehouse IS NULL or ledger.actual_qty= 0 THEN 0 ELSE (FLOOR(ledger.actual_qty/bom.bom_qty)) END as enough_parts_to_build,
			CASE WHEN ledger.warehouse IS NULL or ledger.actual_qty= 0 THEN (bom.required_qty - 0) ELSE (FLOOR(CASE WHEN (CASE WHEN bom.required_qty > ledger.actual_qty THEN 0 ELSE (ledger.actual_qty/bom.bom_qty) END) < {qty_to_produce} THEN (bom.required_qty - (CASE WHEN bom.required_qty > ledger.actual_qty THEN 0 ELSE (ledger.actual_qty/bom.bom_qty) END) - ledger.actual_qty) ELSE 0 END)) END as shortage,
			CASE WHEN ledger.warehouse IS NULL or ledger.actual_qty= 0 THEN '{warehouse}' ELSE ledger.warehouse END as warehouse
			from `tabBin` AS ledger 
			RIGHT JOIN (SELECT 
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
			ON bom.item = ledger.item_code where ledger.actual_qty>=0 or (ledger.warehouse= '{warehouse}' or ledger.warehouse IS NULL)
		 """.format(
				qty_field=qty_field,
				conditions=conditions,
				bom=frappe.db.escape(bom),
				qty=qty,
				warehouse=default_warehouse,
				qty_to_produce=qty_to_produce or 1)

	bom_item_list= frappe.db.sql(query, as_dict=True)
	bom_item_list = sorted(bom_item_list, key=itemgetter('in_stock_qty'))
	for items in bom_item_list:
		records.append(items)
		if items.bom_no:
			bom_list.append(items.bom_no)
		if records:
			for i in range(len(records)):
				if records[i].item == items.item and records[i].bom_qty == items.bom_qty and records[i].warehouse == items.warehouse and records[i].in_stock_qty == 0:
					records[i].in_stock_qty = items.in_stock_qty
					records[i].enough_parts_to_build = items.enough_parts_to_build
					records[i].shortage = items.shortage
	
	if len(bom_list)>1:
		condition=f"""SELECT DISTINCT
			explod_item.item_code as item,
			explod_item.description,
			explod_item.stock_qty as bom_qty,
			explod_item.stock_uom  as bom_uom,
			explod_item.stock_qty * {qty_to_produce or 1}/ {qty} as required_qty,
			CASE WHEN ledger.warehouse IS NULL or ledger.actual_qty= 0 THEN 0 ELSE ledger.actual_qty END as in_stock_qty,
			CASE WHEN ledger.warehouse IS NULL or ledger.actual_qty= 0 THEN 0 ELSE (FLOOR(ledger.actual_qty/explod_item.stock_qty)) END as enough_parts_to_build,
			CASE WHEN ledger.warehouse IS NULL or ledger.actual_qty= 0 THEN (explod_item.stock_qty - 0) ELSE (FLOOR (CASE WHEN ( CASE WHEN (explod_item.stock_qty * {qty_to_produce or 1}/ {qty}) > ledger.actual_qty THEN 0 ELSE (ledger.actual_qty/explod_item.stock_qty) END) < {qty_to_produce} THEN (explod_item.stock_qty * {qty_to_produce or 1}/ {qty}) - ( CASE WHEN (explod_item.stock_qty * {qty_to_produce or 1}/ {qty}) > ledger.actual_qty THEN 0 ELSE (ledger.actual_qty/explod_item.stock_qty) END) - ledger.actual_qty ELSE 0 END)) END as shortage,
			CASE WHEN ledger.warehouse IS NULL or ledger.actual_qty= 0 THEN '{default_warehouse}' ELSE ledger.warehouse END as warehouse
		FROM
			`tabBOM Explosion Item` AS explod_item 
		LEFT JOIN `tabBin` AS ledger
				ON explod_item.item_code = ledger.item_code WHERE
			explod_item.parent in {frappe.db.escape(tuple(bom_list))} or explod_item.parent={filters.get("bom")}
			and ledger.actual_qty >= 0 or (ledger.warehouse= '{default_warehouse}' or ledger.warehouse IS NULL) """
	else:
		condition=f"""SELECT DISTINCT
			explod_item.item_code as item,
			explod_item.description,
			explod_item.stock_qty as bom_qty,
			explod_item.stock_uom  as bom_uom,
			explod_item.stock_qty * {qty_to_produce or 1}/ {qty} as required_qty,
			CASE WHEN ledger.warehouse IS NULL or ledger.actual_qty= 0 THEN 0 ELSE ledger.actual_qty END as in_stock_qty,
			CASE WHEN ledger.warehouse IS NULL or ledger.actual_qty= 0 THEN 0 ELSE (FLOOR( ledger.actual_qty/explod_item.stock_qty) END as enough_parts_to_build,
			CASE WHEN ledger.warehouse IS NULL or ledger.actual_qty= 0 THEN (explod_item.stock_qty - 0) ELSE (FLOOR (CASE WHEN ( CASE WHEN (explod_item.stock_qty * {qty_to_produce or 1}/ {qty}) > ledger.actual_qty THEN 0 ELSE (ledger.actual_qty/explod_item.stock_qty) END) < {qty_to_produce} THEN (explod_item.stock_qty * {qty_to_produce or 1}/ {qty}) - ( CASE WHEN (explod_item.stock_qty * {qty_to_produce or 1}/ {qty}) > ledger.actual_qty THEN 0 ELSE (ledger.actual_qty/explod_item.stock_qty) END) - ledger.actual_qty ELSE 0 END)) END as shortage,
			CASE WHEN ledger.warehouse IS NULL or ledger.actual_qty= 0 THEN '{default_warehouse}' ELSE ledger.warehouse END as warehouse
		FROM
			`tabBOM Explosion Item` AS explod_item 
		LEFT JOIN `tabBin` AS ledger
				ON explod_item.item_code = ledger.item_code WHERE
			explod_item.parent = {frappe.db.escape(tuple(bom_list))} or explod_item.parent={filters.get("bom")}
			and ledger.actual_qty >= 0 or (ledger.warehouse='{default_warehouse}' or ledger.warehouse IS NULL)"""
	
	exploded_item_list= frappe.db.sql(query, as_dict=True)
	for items in exploded_item_list:
		if items not in records and items.in_stock_qty>0 :
			records.append(items)
			if records:
				for i in range(len(records)):
					print(records[i].item)
					if records[i].item == items.item and records[i].bom_qty == items.bom_qty and records[i].warehouse == items.warehouse:
						records[i].in_stock_qty = items.in_stock_qty
						records[i].enough_parts_to_build = items.enough_parts_to_build
						records[i].shortage = items.shortage
	
	records = [dict(t) for t in {tuple(d.items()) for d in records}]

	return records