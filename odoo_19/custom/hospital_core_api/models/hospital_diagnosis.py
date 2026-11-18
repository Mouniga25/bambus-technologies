from odoo import api, fields, models
from datetime import datetime



class HospitalDiagnosis(models.Model):
    _name = 'hospital.diagnosis'
    _description = "Hospital Diagnosis"


    name  = fields.Char(string="Name")
    description = fields.Text(string="Description")



