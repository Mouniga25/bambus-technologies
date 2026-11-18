from odoo import api, fields, models
from datetime import date
from odoo.exceptions import ValidationError



class HospitalLabResult(models.Model):
    _name = 'hospital.lab.result'
    _description = "Hospital Lab Result"
    _rec_name ="doctor_id"


    reference = fields.Char(string="Reference",required=True,copy=False,readonly=True,default="New")
    patient_id = fields.Many2one('res.partner',string="Patient Name", required=True,domain =[("is_patient", "=", True)])
    doctor_id = fields.Many2one('hospital.doctor',string="Doctor Name")
    lab_test_id = fields.Many2one('hospital.lab.test',string="Lab Test")
    visit_id = fields.Many2one('hospital.patient.visit',string="Visit")
    test_id = fields.Many2one('hospital.lab.test',string="Test")

    patient_status = fields.Selection([('normal','Normal'),
                                ('critical','Critical')], string ="Patient Status", default="normal")
    test_name = fields.Char(string="Test Name")
    test_date = fields.Date(string="Test Date")
    price = fields.Float(string="Price")
    description = fields.Text(string="Description")
    doctor_remark = fields.Text()
    result = fields.Float(string="Result")
    unit = fields.Char(string="Unit")
    reference_range=fields.Char(string="Reference Range")
    # lab_results_lines = fields.One2many("hospital.lab.result","primary_doctor_id")
    # patient_visits_lines = fields.One2many("hospital.patient.visit","primary_doctor_id")
    amount_status = fields.Selection([('pending','Pending'),
                                ('completed','Completed')], string ="Amount Status", default="pending")
    high_risk_patient = fields.Boolean(string ="High Risk Patient")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'New') == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'hospital.lab.result'
                ) or 'New'
        return super().create(vals_list)


    @api.constrains("reference")
    def _check_reference_unique(self):
        for rec in self:
            if rec.reference:
                count = self.search_count([
                    ('reference', '=', rec.reference),
                    ('id', '!=', rec.id)
                ])

    """Future test date not allow"""
    @api.constrains("test_date")
    def _check_test_date(self):
        for rec in self:
            if rec.test_date and rec.test_date > date.today():
                raise ValidationError("Future test date is not allowed")


    """Doctor is mandatory"""
    @api.constrains("doctor_id")
    def _check_doctor(self):
        for rec in self:
            if not rec.doctor_id:
                raise ValidationError("Doctor is mandatory.")
    
    
    """Negative Result validation"""
    @api.constrains("result")
    def _check_result(self):
        for rec in self:
            if rec.result < 0:
                raise ValidationError("Negative Result is not allowed")
    
    """Critical result must include doctor's remarks"""
    @api.constrains("patient_status","doctor_remark")
    def _check_remark(self):
        for rec in self:
            if rec.patient_status == "critical" and not rec.doctor_remark:
                raise ValidationError("Doctor remark is mandatory for the criticel results")
            
    #########
    #ACTION
    #########
    def action_pending(self):
        self.write({'amount_status': 'pending'})
    def action_completed(self):
        self.write({'amount_status': 'completed'})