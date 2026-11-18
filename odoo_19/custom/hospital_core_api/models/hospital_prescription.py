from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError



class HospitalPrescription(models.Model):
    _name = 'hospital.prescription'
    _description = "Hospital Prescription"
    _rec_name = "doctor_id"


    patient_id = fields.Many2one('res.partner',string="Patient", required=True,domain =[("is_patient", "=", True)])
    doctor_id = fields.Many2one('hospital.doctor',string="Doctor Name")
    med_name = fields.Char(string="Medicine Name")
    timing = fields.Selection([('morning','Morning'),
                                ('afternoor','Afternoor'),
                                ('night','Night')])
    description = fields.Text(string="Description")
    notes = fields.Text(string="Notes")


    """medicine name is required"""
    @api.constrains("med_name")
    def _check_med_name(self):
        for rec in self:
            if not rec.med_name:
                raise ValidationError("Medicine name is required")
    
    