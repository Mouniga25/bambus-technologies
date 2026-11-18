from odoo import api, fields, models
from datetime import datetime



class ContactsInfo(models.Model):
    _inherit = 'res.partner'



    is_patient = fields.Boolean(string="Is Patient", required = True)
    patient_id = fields.Char(string="Patient ID",required=True, copy=False, readonly=True, default='New')
    blood_group = fields.Selection([('o+','O+'),
                                ('a+','A+'),
                                ('b+','B+'),
                                ('ab-','AB-'),
                                ])
    date_of_birth = fields.Date(string="Date of Birth")
    gender = fields.Selection([('female','Female'),
                                ('male','Male'),
                                ('other','Other')
                                ])
    height = fields.Float(string="Patient Name", required=True)
    weight = fields.Float(string="Patient Name", required=True)
    emergency_contact = fields.Char(string="Patient Name", required=True, size= 10)
    insurance_provider = fields.Text(string="Insurance Provider", required=True)
    insurance_number = fields.Char(string="Patient Name", required=True, size= 12)
    allergies = fields.Text(string="Patient Name", required=True)
    chronic_diseases = fields.Text(string="Chronic Diseases", required=True)
    primary_doctor_id = fields.Many2one('hospital.doctor',string="Primary Doctor")
    last_visit_date = fields.Date(string="Last Visit Date")
    total_visits = fields.Char(compute="_compute_total_visits",store=True) 
    total_lab_tests = fields.Char(compute="_compute_lab_test",store=True)
    lab_results_lines = fields.One2many("hospital.lab.result","primary_doctor_id")
    patient_visits_lines = fields.One2many("hospital.patient.visit","primary_doctor_id")

    """creating sequence number for the patient visit"""
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('patient_id','New') == 'New':
                vals['patient_id'] = self.env['ir.sequence'].next_by_code('res.partner') or 'New'
        return super().create(vals_list)
    

    #####
    # Smart button
    #####
    def action_view_visits(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Visits',
            'res_model': 'hospital.patient.visit',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            }
    def action_view_lab_result(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Visits',
            'res_model': 'hospital.lab.result',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            }
    def action_view_prescription(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Visits',
            'res_model': 'hospital.prescription',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            }




    

    





