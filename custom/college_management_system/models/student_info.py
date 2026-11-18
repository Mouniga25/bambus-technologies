
from odoo import api, fields, models
from datetime import date

class StudentInfo(models.Model):
    _name = 'student.info'
    _description = "student Info"

    name = fields.Char(string="College Name")
    last_name=fields.Char(string="Last Name")
    age = fields.Integer(string="Age",
                         compute = "_compute_age",
                          store=True)
    student_department = fields.Char(string="student department")
    dob = fields.Date(string="date of birth")
    gender = fields.Selection([('female','Female'),
                                ('male','Male'),
                                ('other','Other')
                                ])
    percentage = fields.Float(string="mark")
    @api.depends('dob')
    def _compute_age(self):
        print("------self---",self)
        for rec in self:
            if rec.dob:
                today = date.today()
                rec.age = today.year - rec.dob.year
            else:
                rec.age = 0

    department_ids = fields.Many2many(
        'department.info',
        string="Departments"
    ) 
    # department_ids = fields.Many2one(
    #     'department.info',
    #     string="Department"
    # )
