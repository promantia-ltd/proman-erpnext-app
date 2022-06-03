# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = '0.0.1'
import erpnext
import erpnext.regional.india.utils as erp
from proman.proman.doctype.address.address import validate_gstin

erp.validate_gstin_for_india=validate_gstin
