from odoo import models, fields

class CustomerInfo(models.Model):
    _name = "customer.info"
    _description = "Customer Info"

    name = fields.Char(string="Name",required=True)
    phone = fields.Char(string="Phone",required=True )
    email = fields.Char(string="Email")
    address = fields.Text(string="Address")
    driving_license_no = fields.Char(string="Driving License No",required=True)