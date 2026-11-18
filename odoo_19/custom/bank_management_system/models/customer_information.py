from odoo import api, fields, models
from datetime import date
from odoo.exceptions import ValidationError

class CustomerInformation(models.Model):
    _name = 'customer.information'
    _description = "Customer Information"



    name = fields.Char(string="Name")
    last_name=fields.Char(string="Last Name")
    photo = fields.Binary(string ="Image")
    kyc_status = fields.Selection([('pending','Pending'),
                                    ('verified','Verified'),
                                ('rejected','Rejected')])
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(string="Age")
    gender = fields.Selection([('female','Female'),
                                ('male','Male'),
                                ('other','Other')
                                ])
    
    home_branch_id = fields.Many2one(
        'branch.information',
        string="Home Branch"
    )
    customer_accounts_lines = fields.One2many(comodel_name="bank.accounts",inverse_name = 'customer_id', string="Customer Accounts")
    

    nominee_details_lines = fields.One2many(
    'customer.nominee.line',
    'customer_id',
    string="Nominee Details")
    

    address = fields.Char(string="Address")
    phone = fields.Char(string="Phone")
    alternate_phone = fields.Char(string="Alternate Phone")
    

    """Onchange using age calculation"""
    @api.onchange('date_of_birth')
    def _onchange_age(self):
        for record in self:
            if record.date_of_birth:
                today = date.today()
                record.age = today.year - record.date_of_birth.year
            else:
                record.age = 0

    @api.constrains('nominee_details_lines')
    def _check_nominee_share(self):
        for record in self:
            total_share = sum(record.nominee_details_lines.mapped('share_percentage'))
            if total_share > 100:
                raise ValidationError("Total Nominee Share Percentage cannot exceed 100%.")





class CustomerNomineeLine(models.Model):
    _name = 'customer.nominee.line'
    _description = 'Customer Nominee Details'


    customer_id = fields.Many2one(
        'customer.information',
        string="Customer",
        ondelete='cascade'
    )
    nominee_name = fields.Char(string="Nominee Name")
    relationship = fields.Selection([('spouse','Spouse'),
                                    ('child','Child'),
                                ('parent','Parent'),
                                ('other','Other')])
    share_percentage = fields.Integer(string="share_percentage")
    phone = fields.Char(string="Phone")


    @api.constrains('share_percentage')
    @api.constrains('share_percentage')
    def _share_percentage(self):
        for rec in self:
            if rec.share_percentage > 100:
                raise ValidationError("Share percentage cannot exceed 100%.")
                 
            









    




 
    



