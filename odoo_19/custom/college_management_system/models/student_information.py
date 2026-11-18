from odoo import api, fields, models
from datetime import date
from odoo.exceptions import ValidationError

class StudentInformation(models.Model):
    _name = 'student.information'
    _description = "student information"




    name = fields.Char(string="Name")
    last_name=fields.Char(string="Last Name")
    semester= fields.Selection([('semester_1','Semester_1'),
                                ('semester_2','Semester_2'),
                                ('semester_3','Semester_3'),
                                ('semester_4','Semester_4'),
                                ('semester_5','Semester_5'),
                                ('semester_6','Semester_6')
                                ])
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(string="Age",
                         compute = "_compute_age",
                          store=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('cancel', 'Cancel')], default="draft")
    gender = fields.Selection([('female', 'Female'),('male', 'Male'),('other', 'Other'),], string="Gender")
    department_id = fields.Many2one(
        'department.information',
        string="Department"
    )
    department_date = fields.Date(related="department_id.department_date")
    
    address = fields.Char(string="Address")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    active = fields.Boolean(string = "Active", default=True)
    image = fields.Binary(string="Image")
    guardian_name = fields.Char(string="Guardian Name")
    guardian_relationship = fields.Selection([('father', 'Father'),('mother', 'Mother'),('guardian', 'Guardian'),('other', 'Other'),], string="Relationship")
    guardian_phone = fields.Char(string="Guardian Phone")



    student_count = fields.Integer(compute="_compute_student_count")



    #########
    # Compute
    #########
    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth:
                today = date.today()
                record.age = (
                    today.year - record.date_of_birth.year - ((today.month, today.day) < (record.date_of_birth.month, record.date_of_birth.day)))
            else:
                record.age = 0

    #######
    # ORM
    #######

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'email' in vals and not vals.get('email'):
                raise ValidationError("An email address is mandatory for new partners.")
            if vals.get('email'):
                vals['email'] = vals['email'].lower()
        records = super().create(vals_list)
        return records
     

    def write(self, vals):
        if vals.get('name'):
            vals['name'] = vals['name'].strip().title()
        return super().write(vals)


    def unlink(self):
        if self.state == "confirm":
            raise ValidationError("it's confirm record we can't delete")
        return super().unlink()

    def copy(self, default=None):
        default = dict(default or {})
        
        if 'name' not in default:
            default['name'] = f"{self.name} (Copy)"
        return super().copy(default=default)
    



    #########
    # Action
    #########

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_confirm(self):
        self.write({'state': 'confirm'})

        faculty_id = self.env['faculty.information'].browse(8).read(['name', 'email'])
        print(faculty_id,'-----------------Faulty----search-------------')

        order_ids = self.env['faculty.information'].search([])
        print(self,"----------mapping-----------------------")
        customer_names = order_ids.mapped('name')
        print(customer_names)


    def action_cancel(self):
        self.write({'state': 'cancel'})


    @api.constrains('age')
    def _check_age(self):
        for rec in self:
            if rec.age < 16:
                raise ValidationError("Student must be at least 16 years old for admission.")
    

   



