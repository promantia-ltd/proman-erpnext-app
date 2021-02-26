import frappe
from frappe.core.doctype.communication.email import make
from frappe import _
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from datetime import date, timedelta
import json


@frappe.whitelist()
def purchase_receipt_on_submit(doc):
    rejected_items = []
    try:
        doc = json.loads(doc)
    except:
        doc = None
    if doc is not None:
        for item in doc['items']:
            if item['rejected_warehouse'] is not None:
                item_str = str(item['item_code'] + ' : ' + item['item_name'])
                rejected_items.append(item_str)

    if len(rejected_items) != 0:
        item_str = '\n'.join(rejected_items)
        content = f"""Dear Sir/Ma'am,
                    The following items are sent to Rejected Warehouse,
                        {item_str}

                    Thanks
                    """
        query = """select distinct r.parent from `tabHas Role` r, `tabUser` p where p.name = r.parent and p.enabled = 1 and p.docstatus < 2 and r.role in ('Accounts Manager', 'Purchase Manager', 'HQ') and p.name not in ('Administrator', 'All', 'Guest')"""
        email_list = frappe.db.sql_list(query)
        try:
            make(content=content, subject=f'Rejected Items in {doc["name"]}', send_email=True, recipients=email_list)
        except:
            frappe.msgprint('Could not send email')
    
# @frappe.whitelist()
# def send_notification_on_unpaid_sales_invoice(self, method): # self, method
#     records = frappe.get_all('Sales Invoice', {'posting_date': ['<=', date.today() - timedelta(days=0)], 'status': 'Unpaid'})
#     # query = """select distinct r.parent from `tabHas Role` r, `tabUser` p where p.name = r.parent and p.enabled = 1 and p.docstatus < 2 and r.role='Sales Engineer' and p.name not in ('Administrator', 'All', 'Guest')"""
#     # roles = frappe.db.sql_list(query)
#     if len(records) != 0:
#         for r in records:
#             record = frappe.get_doc('Sales Invoice', r, ['*'])
#             sales_persons_list = [r.sales_person for r in record.sales_team]
#             if len(sales_persons_list) != 0:
#                 employee_id_list = frappe.get_list('Sales Person', filters={'sales_person_name': ['in', sales_persons_list], 'enabled': 1}, fields=['employee'])
#                 employee_id_list = [e.employee for e in employee_id_list]
#                 if len(employee_id_list) != 0:
#                     email_list = frappe.get_list('Employee', filters={'name': ['in', employee_id_list], 'status': 'Active'}, fields=['company_email'])
#                     email_list = [e.company_email for e in email_list]
#                     if len(email_list) !=0:
#                         content = """
#                                 <h1><strong>Sales Invoice Reminder</strong></h1>
#                                 <h2><span style="color: rgb(102, 185, 102);">Sales Invoice Details:</span>
#                                 </h2><table class="table table-bordered"><tbody>
#                                 <tr><td data-row="insert-column-right"><strong>Sales Invoice Due</strong></td>
#                                 <td data-row="insert-column-right"><strong style="color: rgb(107, 36, 178);">{name}</strong></td>
#                                 </tr><tr><td data-row="insert-row-below"><strong>Customer Name</strong></td>
#                                 <td data-row="insert-row-below"><strong style="color: rgb(107, 36, 178);">{customer_name}</strong></td></tr>
#                                 <tr><td data-row="insert-column-right"><strong>Due Date</strong></td>
#                                 <td data-row="insert-column-right"><strong style="color: rgb(107, 36, 178);">{due_date}</strong></td>
#                                 </tr><tr><td data-row="row-zajk">
#                                 <strong>View Document in ERPNext</strong></td><td data-row="row-mze0">
#                                 <strong style="color: rgb(230, 0, 0);"><a href="{link}" target="_blank" class="btn btn-success">Click to view document</a></strong></td></tr><tr><td data-row="row-779i">
#                                 <strong>Note</strong></td><td data-row="row-779i">
#                                 <strong style="color: rgb(255, 153, 0);">This is a system generated email, please don't reply to this message.</strong></td></tr></tbody></table>
#                         """.format(name=record.name, customer_name=record.customer_name, due_date=frappe.utils.formatdate(record.get_formatted('due_date'), "dd-mm-yyyy"),
#                                     link=frappe.utils.get_url_to_form(record.doctype, record.name))
#                         make(content=content, subject="Payment due reminder.", recipients=email_list, send_email=True)
