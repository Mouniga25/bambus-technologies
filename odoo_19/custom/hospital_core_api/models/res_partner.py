from odoo import api, fields, models
from datetime import date
from odoo.exceptions import ValidationError



class ContactsInfo(models.Model):
    _inherit = 'res.partner'

    
    #sequence
    patient_number = fields.Char(string="Patient Number",required=True, copy=False, readonly=True, default='New')

    is_patient = fields.Boolean(string="Is Patient")
   
    department_id = fields.Many2one('hospital.department',string="Department")
    patient_name = fields.Char(string="Patient Name")
    blood_group = fields.Selection([('o+','O+'),
                                ('a+','A+'),
                                ('b+','B+'),
                                ('ab-','AB-'),
                                ])
    
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(string ="Age", compute="_compute_age", store=True)
    gender = fields.Selection([('female','Female'),
                                ('male','Male'),
                                ('other','Other')
                                ])
    
    height = fields.Float(string="Height" )
    weight = fields.Float(string="Weight")
    bmi = fields.Float(string = "BMI", compute ="_compute_bmi", store=True)
    emergency_contact = fields.Char(string="Emergency Contact", size= 10)
    insurance_provider = fields.Text(string="Insurance Provider")
    insurance_number = fields.Char(string="Insurance Number", size= 12)
    allergies = fields.Text(string="Allergies")
    chronic_diseases = fields.Text(string="Chronic Diseases")
    primary_doctor_id = fields.Many2one('hospital.doctor',string="Primary Doctor")
    last_visit_date = fields.Date(string="Last Visit Date")

    # total_visits = fields.Char(compute="_compute_total_visits",store=True) 
    # total_lab_tests = fields.Char(compute="_compute_lab_test",store=True)

    total_visits =fields.Integer(string="Total Visit", compute="_compute_total_counts", store=True)
    total_lab_tests = fields.Integer(string = "Total Lab Test", compute="_compute_total_counts",store=True)
    medical_notes = fields.Text(string="Medical Notes")

    visits_count = fields.Integer(compute="_compute_counts")
    lab_result_count = fields.Integer(compute="_compute_counts")
    prescription_count = fields.Integer(compute="_compute_counts")



    visits_count_lines = fields.One2many('hospital.patient.visit', 'patient_id')
    lab_result_count_lines = fields.One2many('hospital.lab.result', 'patient_id')
    lab_test_count_lines = fields.One2many('hospital.lab.test', 'patient_id')
    prescription_count_lines = fields.One2many('hospital.prescription', 'patient_id')

    doctor_count= fields.Integer(string="Doctors",compute="_compute_counts")
    patient_count= fields.Integer(string="Patient",compute="_compute_counts")

    
    """creating sequence number for the patient visit"""
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('patient_number','New') == 'New':
                vals['patient_number'] = self.env['ir.sequence'].next_by_code('res.partner') or 'New'
        return super().create(vals_list)
    
    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth:
                today = date.today()
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 0 

    """DOB cannot be in the future"""
    @api.constrains("date_of_birth")
    def _check_dob(self):
        for rec in self:
            if rec.date_of_birth and rec.date_of_birth > date.today():
                raise ValidationError("DOB cannot be in the future")
    

    """emergency_contact is reuired"""
    @api.constrains("emergency_contact")
    def _check_emergency_contact(self):
        for rec in self:
            if rec.is_patient and not rec.emergency_contact:
                raise ValidationError("emergency_contact is required")
            
            
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
            'name': 'Lab Result',
            'res_model': 'hospital.lab.result',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            }
    def action_view_prescription(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescription',
            'res_model': 'hospital.prescription',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            }


    ############
    # action
    #############
    def action_click(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hospital Followup',
            'res_model': 'hospital.followup.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
            'default_patient_id': self.id
            }
        }
    

    """count the record"""
    @api.depends('visits_count_lines','lab_result_count_lines','prescription_count_lines','lab_test_count_lines')
    def _compute_counts(self):
        for rec in self:
            rec.visits_count = self.env['hospital.patient.visit'].search_count([('patient_id', '=', rec.id)])
            rec.lab_result_count = self.env['hospital.lab.result'].search_count([('patient_id', '=', rec.id)])
            rec.prescription_count = self.env['hospital.prescription'].search_count([('patient_id', '=', rec.id)])

    @api.depends('visits_count_lines','lab_test_count_lines')
    def _compute_total_counts(self):
        for rec in self:
            rec.total_visits = len(rec.visits_count_lines)
            rec.total_lab_tests = len(rec.lab_test_count_lines)


    @api.constrains('patient_id')
    def _check_patient_id_unique(self):
        for rec in self:
            if rec.patient_id:
                count = self.env['res.partner'].search_count([
                    ('patient_id', '=', rec.patient_id),
                    ('id', '!=', rec.id)
                ])

                if count:
                    raise ValidationError("Patient ID must be unique.")

    @api.constrains('insurance_number')
    def _check_insurance_number_unique(self):
        for rec in self:
            if rec.insurance_number:
                count = self.env['res.partner'].search_count([
                    ('insurance_number', '=', rec.insurance_number),
                    ('id', '!=', rec.id)
                ])
                if count:
                    raise ValidationError("Insurance Number must be unique.")

           
    @api.depends("height","weight")
    def _compute_bmi(self):
        for rec in self:
            if rec.height and rec.weight:
                rec.bmi = rec.weight /(rec.height) ** 2
            else:
                 rec.bmi = 0.0


class ContactsInfoLine(models.Model):
    _name = 'contacts.info.line'
    _description = 'Contacts Info'

    primary_doctor_id = fields.Many2one('hospital.doctor',string="Primary Doctor")




    

    





