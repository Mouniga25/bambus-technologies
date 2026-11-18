from odoo import api, fields, models
from datetime import datetime



class HospitalDepartment(models.Model):
    _name = 'hospital.department'
    _description = "Hospital Department"
    _rec_name = "department_name"


    department_name = fields.Char(string="Department Name", required=True)
    department_code = fields.Char(string="Department Code")
   

    doctor_lines = fields.One2many('hospital.doctor', 'department_id')
    patient_lines = fields.One2many('res.partner', 'department_id')

    doctor_counts= fields.Integer(string="Doctor",compute="_compute_counts")
    patient_counts= fields.Integer(string="Patient",compute="_compute_counts")


    # doctor_lines = fields.One2many("hospital.doctor","department_id", string="Doctors")



    #compute  fields 
    @api.depends('doctor_counts', 'patient_counts') 
    def _compute_counts(self):
        for rec in self:
            rec.doctor_counts =self.env["hospital.doctor"].search_count([('department_id', '=', rec.id)])
            rec.patient_counts = self.env["res.partner"].search_count([('department_id', '=', rec.id)])
    
    ########
    # smart button 
    ##########
    def action_view_doctors(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Doctor',
            'res_model': 'hospital.doctor',
            'view_mode': 'list,form',
            'domain': [('department_id', '=', self.id)],
            }
    def action_view_patient(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Patient',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [('department_id', '=', self.id)],
            }



    

