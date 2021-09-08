# -*- coding: utf-8 -*-
# Copyright (c) 2021, proman_app and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document

class ItemStockUpdate(Document):
	pass

@frappe.whitelist()
def get_warehouses(doc,method):
	warehouses=frappe.db.sql("""SELECT item_code,sum(stock_value_difference) as stock_value ,warehouse 
		FROM `tabStock Ledger Entry` GROUP BY item_code,warehouse having sum(stock_value_difference)<0
		and item_code=%s""",doc.item_code,as_dict=True)
	for warehouse in warehouses:
		doc.append('stock_warehouse', {
			'warehouse':warehouse.warehouse,
			'stock_value_difference':warehouse.stock_value
		})

@frappe.whitelist()
def update_stock_difference(doc,method):
	warehouses=frappe.db.sql("""SELECT item_code,sum(stock_value_difference) as stock_value ,warehouse 
		FROM `tabStock Ledger Entry` GROUP BY item_code,warehouse having sum(stock_value_difference)<0
		and item_code=%s""",doc.item_code,as_dict=True)
	if warehouses:
		for warehouse in warehouses:
			print(warehouse.warehouse)
			warehouses=frappe.db.sql("""UPDATE `tabStock Ledger Entry` SET stock_value_difference=0
			where item_code=%s and warehouse = %s
			""",(doc.item_code,warehouse.warehouse))
	else:
		frappe.throw('Item '+doc.item_code+' does not have negative stock value difference')

