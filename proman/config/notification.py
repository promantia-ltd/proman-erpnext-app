import frappe
from frappe.core.doctype.communication.email import make
from frappe import _
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from datetime import date, timedelta
import json


@frappe.whitelist()
def lead_notify_on_save(recipients, phone, mobile_no):
    if recipients is not None:
        full_name = ''
        name = frappe.get_doc('User', {'email': recipients}, ['*']).as_dict()
        try:
            content = f"""Dear Sales Engineer,
                        The {name.full_name} Lead is assigned to you for communication and followup. Please do the needful.
                        Regards,

                        CRM Team
                        """
            # subject = 'Lead Assignment'
            ##### if email notification is required
            # make(content=content, subject=subject, send_email=True)
            if mobile_no is not None:
                send_sms([int(mobile_no)], content)
        except:
            frappe.msgprint('Could not send the Message')

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
        email_list = frappe.db.sql_list("""select distinct r.parent
            from `tabHas Role` r, tabUser p
            where p.name = r.parent and p.enabled = 1 and p.docstatus < 2
            and r.role in ('Accounts Manager', 'Purchase Manager', 'HQ')
            and p.name not in ('Administrator', 'All', 'Guest')""")
        try:
            make(content=content=, subject=f'Rejected Items in {doc['name']}', send_email=True, recipients=email_list)
        except:
            frappe.msgprint('Could not send email')


@frappe.white_list()
def 