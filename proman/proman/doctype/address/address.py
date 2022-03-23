from erpnext.regional.india.utils import set_gst_state_and_state_number
import frappe
import re
from frappe import _
from erpnext.regional.india import state_numbers
GST_INVOICE_NUMBER_FORMAT = re.compile(r"^[a-zA-Z0-9\-/]+$")   #alphanumeric and - /
GSTIN_FORMAT = re.compile("^[0-9]{2}[A-Z]{4}[0-9A-Z]{1}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[1-9A-Z]{1}[0-9A-Z]{1}$")
GSTIN_UIN_FORMAT = re.compile("^[0-9]{4}[A-Z]{3}[0-9]{5}[0-9A-Z]{3}")
PAN_NUMBER_FORMAT = re.compile("[A-Z]{5}[0-9]{4}[A-Z]{1}")


def validate_gstin(doc, method):
	if hasattr(doc, 'gst_state') and doc.gst_state:
		doc.gst_state_number = state_numbers[doc.gst_state]
	if not hasattr(doc, 'gstin') or not doc.gstin:
		return

	gst_category = []

	if hasattr(doc, 'gst_category'):
		if len(doc.links):
			link_doctype = doc.links[0].get("link_doctype")
			link_name = doc.links[0].get("link_name")

			if link_doctype in ["Customer", "Supplier"]:
				gst_category = frappe.db.get_value(link_doctype, {'name': link_name}, ['gst_category'])

	doc.gstin = doc.gstin.upper().strip()
	if not doc.gstin or doc.gstin == 'NA':
		return

	if len(doc.gstin) != 15:
		frappe.throw(_("A GSTIN must have 15 characters."), title=_("Invalid GSTIN"))

	if gst_category and gst_category == 'UIN Holders':
		if not GSTIN_UIN_FORMAT.match(doc.gstin):
			frappe.throw(_("The input you've entered doesn't match the GSTIN format for UIN Holders or Non-Resident OIDAR Service Providers"),
				title=_("Invalid GSTIN"))
	else:
		#if not GSTIN_FORMAT.match(doc.gstin):
			#frappe.throw(_("The input you've entered doesn't match the format of GSTIN."), title=_("Invalid GSTIN"))

		#validate_gstin_check_digit(doc.gstin)
		set_gst_state_and_state_number(doc)

		if not doc.gst_state:
			frappe.throw(_("Please enter GST state"), title=_("Invalid State"))

		if doc.gst_state_number != doc.gstin[:2]:
			frappe.throw(_("First 2 digits of GSTIN should match with State number {0}.")
				.format(doc.gst_state_number), title=_("Invalid GSTIN"))

