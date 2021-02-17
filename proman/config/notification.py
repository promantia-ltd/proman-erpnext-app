import frappe
from frappe.core.doctype.communication.email import make
from frappe import _
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from datetime import date, timedelta


@frappe.whitelist()
def lead_notify_on_save(recipients, phone, mobile_no):
    if recipients is not None:
        full_name = ''
        name = frappe.get_doc('User', {'email': recipients}, ['*']).as_dict()
        try:
            ##### if email notification is required
            # content = f"""Dear Sales Engineer,
            #             The {full_name} Lead is assigned to you for communication and followup. Please do the needful.
            #             Regards,

            #             CRM Team
            #             """
            # subject = 'Lead Assignment'
            # make(content=content, subject=subject, send_email=True)
            if mobile_no is not None:
                send_sms([int(mobile_no)], content)
        except:
            frappe.msgprint('Could not send the Email')