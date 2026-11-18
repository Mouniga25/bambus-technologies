from odoo import api, fields, models
from datetime import date

class AccountType(models.Model):
    _name = 'account.type'
    _description = "Account Type"
    _rec_name ="type_name"



    type_code = fields.Char(string="Type Code")
    type_name = fields.Selection([('savings','Savings'),
                                ('current','Current'),
                                ('fixed_deposit','Fixed Deposit')
                                ])
    interest_rate = fields.Float(string="Interest Rate")





