from __future__ import unicode_literals
from frappe import _

def get_dashboard_data(data):
	return {
		'fieldname': 'production_plan',
		'transactions': [
			{
				'label': _('Transactions'),
				'items': ['Work Order', 'Material Request', 'Service Request']
			},
		]
	}
