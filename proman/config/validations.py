from datetime import date
from datetime import datetime
import frappe

def validate_employee_posting_date(self, method):
    try:
        self.posting_date = datetime.strptime(self.posting_date, '%Y-%m-%d').date()
    except:
        pass
    if self.posting_date < date.today():
        frappe.throw("Today's date value cannot be less than the today's date")