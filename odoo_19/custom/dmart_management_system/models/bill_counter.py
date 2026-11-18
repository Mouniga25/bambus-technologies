from odoo import api, fields, models
from datetime import datetime



class BillCounter(models.Model):
    _name = 'bill.counter'
    _description = "Bill Counter"
    _rec_name = "customer_name"

    user_id = fields.Many2one( 
        'res.users',
        string='User',
        default=lambda self: self.env.user
    )

    counter_code = fields.Char(string="Counter Code")
    customer_name = fields.Char(string="Customer Name")
    employee_name = fields.Char(string="Employee Name")
    location = fields.Char(string="Location")
    opening_time = fields.Datetime(string="Opening Time",required=True)
    closing_time = fields.Datetime(string="Closing Time",required=True)
    total_kg = fields.Float(string="Total KG")
    total_number = fields.Float(string="Total Number")


class ResUsers(models.Model):
    _inherit = "res.users"

    is_manager = fields.Boolean(string="Is Manager")

    manager_id = fields.Many2one('res.users',string="Manager",domain=[('is_manager', '=', True)])










