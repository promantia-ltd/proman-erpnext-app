from __future__ import unicode_literals
from frappe import _


def get_dashboard_data(data):
	return {
		'fieldname': 'service_request',
		'transactions': [
			{
				'label': _('Related'),
				'items': ['Purchase Order']
			}
		]
	}
