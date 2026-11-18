from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError



class HospitalDoctor(models.Model):
    _name = 'hospital.doctor'
    _description = "Hospital Doctor"
    _rec_name = "doctor_name"         


    #doctor details
    doctor_name = fields.Char(string="Doctor Name",  required=True)
    department_id = fields.Many2one('hospital.department',string="Department")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone", size=10)
    description = fields.Text(string="Description")
    patient_lines = fields.One2many("res.partner","primary_doctor_id")
    patient_count = fields.Integer(string="Assigned Patients",compute="_compute_counts")
    pending_lab_count = fields.Integer(string="Pending Lab Results",compute="_compute_counts")

    user_id = fields.Many2one(
    'res.users',
    string="User"
)

    """phone number will be unique"""
    @api.constrains("phone")
    def _check_phone(self):
        for rec in self:
            if rec.phone:
                duplicate_phone = self.search_count([
                    ("phone", "=", rec.phone),
                    ("id", "!=", rec.id)
                ])

                if duplicate_phone:
                    raise ValidationError("Phone number must be unique.")

    def _compute_counts(self):
        for rec in self:
            rec.patient_count = self.env['res.partner'].search_count([
                ('primary_doctor_id', '=', rec.id)
            ])

            rec.pending_lab_count = self.env['hospital.lab.result'].search_count([
                ('doctor_id', '=', rec.id),
                ('amount_status', '=', 'pending')
            ])

    def action_view_patients(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assigned Patients',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [
                ('primary_doctor_id', '=', self.id)
            ],
        }
    def action_view_pending_lab_results(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pending Lab Results',
            'res_model': 'hospital.lab.result',
            'view_mode': 'list,form',
            'domain': [
                ('doctor_id', '=', self.id),
                ('amount_status', '=', 'pending')
            ],
        }

    