from __future__ import unicode_literals
import frappe, json, copy
from frappe import msgprint, _
from six import string_types, iteritems

from frappe.model.document import Document
from frappe.utils import cstr, flt, cint, nowdate, add_days, comma_and, now_datetime, ceil
from erpnext.manufacturing.doctype.work_order.work_order import get_item_details
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from frappe.model.mapper import get_mapped_doc
from itertools import groupby

class ProductionPlan(Document):
	pass

@frappe.whitelist()
def auto_create_service_request(doc):
	items = []
	itemcodes = []
	subcontracteditem = []
	
	result=json.loads(doc)
	for dicts in frappe.db.get_list("Production Plan Item", filters={"parent":result['name'],"make_service_request_for_subcontracted_items":1,"warehouse":["!=",""]},fields={'*'}):
		items.append(dicts)
		if dicts.bom_no:
			for  item_data in get_items(dicts.bom_no,dicts.planned_qty):
				warehouse={"warehouse":dicts.warehouse}
				quantity={"planned_qty":item_data.qty}
				item_data.update(warehouse)
				item_data.update(quantity)
				items.append(item_data)

	for code in items:
		itemcodes.append(code.item_code)

	for subitem in frappe.db.get_list("Item",filters={"item_code":['in',itemcodes],"is_sub_contracted_item":1},fields={"item_code"}):
		subcontracteditem.append(subitem.item_code)

	for loop_items in range(len(items)):
		for sr_items in items:
			if sr_items['item_code'] not in subcontracteditem:
				items.pop(items.index(sr_items))

	if "project" in result:
		assign_project=result['project']
	else:
		assign_project=""

	sorted_users = sorted(items, key=lambda x: (x['warehouse']))
	grouped_by_supplier = {}
	for key, group in groupby(sorted_users, key=lambda x: (x['warehouse'])):
		grouped_by_supplier[key]= list(group)
	for key,data in grouped_by_supplier.items():
		sr_doc=frappe.get_doc(dict(doctype = 'Service Request',
			material_request_type="Purchase",
			transaction_date=nowdate(),
			schedule_date=nowdate(),
			production_plan=result['name'],
			project=assign_project
		))#.insert(ignore_mandatory=True)
		for val in data:
			sr_doc.append('items', {
				'item_code':val['item_code'],
				'schedule_date':nowdate(),
				'item_name':frappe.db.get_value('Item',{'item_code':val['item_code']},'item_name'),
				'description':frappe.db.get_value('Item',{'item_code':val['item_code']},'description'),
				'qty':val['planned_qty'],
				'stock_qty':val['planned_qty'],
				'stock_uom':val['stock_uom'],
				'uom':val['stock_uom'],
				'conversion_factor':1,
				'warehouse':val['warehouse'],
				'production_plan':result['name']
			})
		sr_doc.save()

	for workorders in frappe.db.get_list("Work Order", filters={"production_item":["in",subcontracteditem],"production_plan":result['name']},fields={'name'}):
		frappe.db.set_value('Work Order', workorders.name,{ 'status': 'Stopped','docstatus': 1})

	lists = frappe.db.get_list("Production Plan Item", filters={"parent":result['name'],"make_service_request_for_subcontracted_items":1,"warehouse":""},fields={'*'})
	no_warehouse_items = []
	for ele in lists:
		no_warehouse_items.append(ele['item_code'])
	if lists:
		msgprint(_("Default Warehouse is unavailable for the Item: {0}. To proceed update the default warehouse for the item.").format(comma_and(no_warehouse_items)))

	service_request_list=frappe.db.get_list("Service Request", filters={"production_plan":result['name']},fields={'name'})
	return service_request_list


def get_items(bom,qty):
	bom_qty = 1
	item_list=[]
	for bom in frappe.db.get_list("BOM Item", filters={"parent":bom}, fields={'*'}):
		added_qty = bom.stock_qty * qty
		bom1 = {"qty":added_qty}
		bom.update(bom1)
		item_list.append(bom)
		if bom.bom_no:
			for child_item_list in get_items(bom.bom_no, bom.qty):
				bom_qty = bom.qty
				child_item_list.qty = child_item_list.stock_qty * bom_qty
				item_list.append(child_item_list)
	return item_list
