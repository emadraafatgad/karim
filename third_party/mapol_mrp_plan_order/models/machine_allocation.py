# -*- coding: utf-8 -*-

from odoo import models, fields, _


class MachineAllocation(models.Model):
    _name = "machine.allocation"
    _description = 'Machine Allocation'
    
    name = fields.Char(string='Machine Name', copy=False, index=True, required=True, translate=True)
    employee_ids = fields.Many2many('hr.employee', string='Resource Allocation')
    total_hours_per_day = fields.Float('Total Hours/Day', required=True)
    date = fields.Date(string='Date',
                       track_visibility='onchange', required=True,
                       default=fields.Date.context_today)
    