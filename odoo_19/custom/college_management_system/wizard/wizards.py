from odoo import api, fields, models


class PopUpInformation(models.TransientModel):
    _name = 'popup.information'
    _description = "Popup Information"

    name = fields.Char(string="Name")
    degree_name =fields.Char(string="Degree Name")
    code = fields.Integer(string="code")
    phone = fields.Char(string="phone")


    
