from odoo import api, fields, models, _, Command


class GraduationInstitute(models.Model):
    _name = 'graduation.institute'
    _description = "Graduation Institute"
    
    name = fields.Char(string="Institute Name")
    institute_code= fields.Integer(string="Institute Code")

    