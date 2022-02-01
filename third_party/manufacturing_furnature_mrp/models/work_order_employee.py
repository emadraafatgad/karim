import pytz
import sys
import datetime
import logging
import binascii
from datetime import date, datetime, time

from struct import unpack
from odoo import api, fields, models
from odoo import _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

class WorkOrderEmployee(models.Model):
    _inherit = 'mrp.workorder'

    employee_id = fields.Many2one('hr.employee',states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})


class EmployeeWeeklySalary(models.Model):
    _inherit = 'hr.payslip'

    total_finished_products = fields.Integer(compute='get_total_finished_products',store=True)

    @api.depends('date_from', 'date_to', 'employee_id')
    def get_total_finished_products(self):
        for rec in self:
            day_from = datetime.combine(fields.Date.from_string(rec.date_from), time.min)
            print(day_from)
            day_to = datetime.combine(fields.Date.from_string(rec.date_to), time.max)
            print(day_to)
            if rec.employee_id:
                workeorders = self.env['mrp.workorder'].search_count(
                    [('employee_id', '=', rec.employee_id.id), ('date_finished', '>=', day_from),
                     ('date_finished', '<=', day_to)])
                print(workeorders, "=========== WorkOrders ============")
                rec.total_finished_products=workeorders