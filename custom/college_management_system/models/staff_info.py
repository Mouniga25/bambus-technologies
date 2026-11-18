from odoo import api, fields, models, _, Command
from datetime import date

class StaffInfo(models.Model):
    _name = 'staff.info'
    _description = "Staff Info"
    
    name = fields.Char(string="Staff Name")
    last_name=fields.Char(string="Last Name")
    age = fields.Integer(string="Age" ,
                         compute ='_compute_age')
    staff_department = fields.Char(string="staff department")
    dob = fields.Date(string="date of birth")
    gender = fields.Selection([('female','Female'),
                                ('male','Male'),
                                ('other','Other')
                                ])
    @api.depends('dob')
    def _compute_age(self):
        for record in self:
            if record.dob:
                today = date.today()
                record.age = today.year - record.dob.year
            else:
                record.age = 0
    department_id =fields.Many2many('department.info', String ="Departments")


    