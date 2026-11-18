from odoo import api, fields, models
from datetime import date

class BranchInformation(models.Model):
    _name = 'branch.information'
    _description = "Branch Information"
    _rec_name ="branch_name"



    branch_code = fields.Char(string="Branch Code")
    branch_name=fields.Char(string="Branch Name")
    manager  = fields.Many2one(
        'employee.information',
        string="Manager"
    )
    location = fields.Char(string="Location")













