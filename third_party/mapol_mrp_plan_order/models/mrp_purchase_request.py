import xlsxwriter
import base64
from odoo import fields, models, api
from io import BytesIO
from datetime import datetime , time ,timedelta
from pytz import timezone
import pytz
import time


class HrAttendanceEmployee(models.TransientModel):

    _name = 'mrp.purchase'
    _description = 'purchase request from all mrp requests'

    date_from = fields.Date(string='From', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='To', required=True,)

