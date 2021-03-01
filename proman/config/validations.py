from datetime import date
from datetime import datetime
import frappe

def validate_employee_posting_date(self, method):
    self.posting_date = datetime.strptime(self.posting_date, '%Y-%m-%d').date()
    if self.posting_date < date.today():
        frappe.throw("Today's date value cannot be less than the today's date")