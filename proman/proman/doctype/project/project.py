from __future__ import unicode_literals
from typing_extensions import IntVar
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class Project(Document):
    pass

def update_gross_margin(self,doc):
    project = None
    if self.doctype == "Timesheet":
        project = self.parent_project
    else:
        project = self.project
    if project:
        proj = frappe.db.get_value('Project', project, ['total_billed_amount','total_billable_amount','total_expense_claim','total_consumed_material_cost'], as_dict=1)
        invoice_amt = frappe.db.sql("""select sum(base_net_total) from `tabSales Invoice` where project = %s and docstatus=1""", project)
        invoice = invoice_amt and invoice_amt[0][0] or [0]
        timesheet = frappe.db.sql("""select sum(billing_amount) as billing_amount from `tabTimesheet Detail` where project = %s and docstatus = 1 """, project, as_dict=1)[0]
        expense = frappe.db.sql("""select sum(total_sanctioned_amount) as total_sanctioned_amount from `tabExpense Claim` where project = %s and docstatus = 1""", self.name, as_dict=1)[0]
        stock = proj.total_consumed_material_cost
        gross_margin = flt(invoice) - flt(timesheet) - flt(expense) - flt(stock)
        gm = gross_margin
        frappe.db.set_value('Project', project, 'gross_margin_amount', gross_margin)
