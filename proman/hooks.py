# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "proman"
app_title = "Proman"
app_publisher = "proman_app"
app_description = "proman_app"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "proman_app@gmail.com"
app_license = "MIT"


fixtures = ["Workflow","Workflow State","Workflow Action Master", "Server Script",
            {"dt": "Property Setter",
             "filters": [
                 [
                     "name", "in", ["Lead-contact_by-reqd",
                                    "Lead-contact_date-reqd",
                                    "Lead-ends_on-reqd",
                                    "Lead-notes-reqd", "Lead-phone-reqd",
                                    "Lead-mobile_no-reqd",
                                    "Lead-fax-reqd",
                                    "Employee-naming_series-label",
                                    "Production Plan-project-mandatory_depends_on",
                                    "Project-gross_margin-hidden",
                                    "Project-per_gross_margin-hidden",
                                    "Timesheet Detail-hours-label",
                                    "Timesheet Detail-hours-columns"
                                    ]
                 ]
             ]},
            {"dt": "Custom Field",
                "filters": [
                    [
                        "name", "in", ["Lead-remarks",
                                       "Lead-influencer",
                                       "Lead-sales_engineer_name",
                                       "Job Applicant-alternate_mail",
                                       "Job Applicant-column_break_20",
                                       "Job Applicant-current_place_of_employment",
                                       "Job Applicant-years_of_experience",
                                       "Job Applicant-column_break_19",
                                       "Job Applicant-comments",
                                       "Job Applicant-more_info",
                                       "Job Applicant-alternate_number",
                                       "Job Applicant-primary_number",
                                       "Job Applicant-primary_mail",
                                       "Job Applicant-personal_details",
                                       "Job Applicant-notice_period_days",
                                       "Job Applicant-date_of_birth",
                                       "Job Applicant-expected_ctc",
                                       "Job Applicant-locality",
                                       "Job Applicant-current_job_title",
                                       "Job Applicant-current_ctc",
                                       "Job Applicant-applicant_details",
                                       "Job Applicant-academic_details_table",
                                       "Job Applicant-academic_details",
                                       "Employee-posting_date",
                                       "Employee-location",
                                       "Employee-ctc_at_the_time_of_joining",
                                       "Employee-current_ctc",
                                       "Employee-confirmation_status",
                                       "Employee Internal Work History-current_experience",
                                       "Employee-age",
                                       "Employee-religion",
                                       "Employee-fathers_name",
                                       "Employee-aadhar_number",
                                       "Employee-uan_number",
                                       "Employee-esi_number",
                                       "Employee-official_contact_number",
                                       "Employee-bank_details",
                                       "Employee-personal_bank_account_number",
                                       "Employee-bank_account_details",
                                       "Employee-bank_address",
                                       "Employee-personal_bank_details",
                                       "Employee-ifs_code",
                                       "Employee-nominee_name",
                                       "Employee-nominee_relation",
                                       "Employee Internal Work History-last_increment_date",
                                       "Employee Internal Work History-last_promotion_date",
                                       "Employee-gratuity",
                                       "Employee External Work History-previous_uan_number",
                                       "Employee-accident_insurance",
                                       "Employee-mobile_number",
                                       "Quality Inspection-heat_number",
                                       "Blanket Order-remarks",
                                       "Quotation-remarks",
                                       "Employee Transfer-remarks",
                                       "Purchase Receipt-supplier_invoice_number",
                                       "Purchase Order Item-service_request",
                                       "Purchase Order Item-service_request_item",
                                       "Production Plan Item-make_service_request_for_subcontracted_items",
                                       "Material Request-project_name",
                                       "Lead-sales_engineer_mobile_no",
                                       "Purchase Order-service_request",
                                       "Purchase Order-project",
                                       "Material Request-project",
                                       "Project-gross_margin_amount",
                                       "Timesheet Detail-individual_hours",
                                       "Timesheet Detail-no_of_workers"
                                       ]
                    ]
                ]},
            {"dt": "Role",
                "filters": [
                    [
                        "name", "in", ["Sales Engineer",
                                       "Quality Persion",
                                       "Vendor Development",
                                       "Sales Co-ordinator",
                                       "General",
                                       "HQ",
                                       "Production User",
                                       "MD",
                                       "ERP User"
                                       ]
                    ]
                ]
             },
            {"dt": "Notification",
                "filters": [
                    "is_standard != 1"
                ]
             },

            {'dt': "Client Script",
                "filters": [
                    [
                        "name", "in", ["Employee-Client",
					"Work Order-Client",
					"Service Request-Form"
                                       ]
                    ]
                ]
             }
            ]
doctype_js = {
	"Production Plan" : "proman/doctype/production_plan/production_plan.js",
    "Project" : "proman/doctype/project/project.js",
    "Delivery Note" : "proman/doctype/delivery_note/delivery_note.js",
    "Quotation" : "proman/doctype/quotation/quotation.js",
    "Timesheet" : "proman/doctype/timesheet/timesheet.js"
}

override_doctype_dashboards = {
	"Production Plan": ["proman.proman.doctype.production_plan.production_plan_dashboard.get_dashboard_data"]
}


doc_events = {
	"Item Stock Update": {
		"before_save": "proman.proman.doctype.item_stock_update.item_stock_update.get_warehouses",
		"on_submit": "proman.proman.doctype.item_stock_update.item_stock_update.update_stock_difference"
	},
    "Sales Invoice":{
        "on_submit":"proman.proman.doctype.project.project.update_gross_margin",
        "on_cancel":"proman.proman.doctype.project.project.update_gross_margin"
    },
    "Timesheet":{
        "on_submit":"proman.proman.doctype.project.project.update_gross_margin",
        "on_cancel":"proman.proman.doctype.project.project.update_gross_margin"
    },
    "Expense Claim":{
        "on_submit":"proman.proman.doctype.project.project.update_gross_margin",
        "on_cancel":"proman.proman.doctype.project.project.update_gross_margin"
    }
}

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/proman/css/proman.css"
# app_include_js = "/assets/proman/js/proman.js"

# include js, css files in header of web template
# web_include_css = "/assets/proman/css/proman.css"
# web_include_js = "/assets/proman/js/proman.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "proman/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "proman.install.before_install"
# after_install = "proman.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "proman.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"proman.tasks.all"
	# ],
	# "daily": [
	# 	"proman.config.notification.send_notification_on_unpaid_sales_invoice"
	# ],
	# "hourly": [
	# 	"proman.tasks.hourly"
	# ],
	# "weekly": [
	# 	"proman.tasks.weekly"
	# ]
	# "monthly": [
	# 	"proman.tasks.monthly"
	# ]
}

# Testing
# -------

# before_tests = "proman.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "proman.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "proman.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]
