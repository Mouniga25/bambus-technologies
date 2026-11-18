from odoo import api, fields, models
from datetime import datetime



class HospitalLabTest(models.Model):
    _name = 'hospital.lab.test'
    _description = "Hospital Lab Test"

    patient_id = fields.Many2one(
    'res.partner',
    string="Patient Name",
    required=True,
    domain=[("is_patient", "=", True)]
)
    name  = fields.Char(string="Name")
    result = fields.Selection([('positive','Positive'),
                                ('negative','Negative')], string = "Result")
    test_category = fields.Selection([('blood','Blood'),('xray','Xray'),('other','Other')], string="Test Category")
    price = fields.Float(string="Price")
    unit = fields.Char(string="Unit")
    reference_range=fields.Char(string="Reference Range")
    description = fields.Char(string="Description")

