import frappe
import json

@frappe.whitelist()
def set_quotation_as_lost(doc_name):
    if doc_name:
        frappe.db.set_value('Quotation', doc_name, 'workflow_state', "Lost")
