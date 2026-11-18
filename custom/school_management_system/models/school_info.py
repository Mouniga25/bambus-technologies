
from odoo import api, fields, models, _, Command


class SchoolInfo(models.Model):
    _name = 'school.info'
    _description = "School Info"
    name = fields.Char(string="School Name")
    last_name=fields.Char(string="Last name")
    age = fields.Integer(string="age")
    student_class = fields.Char(string="student class")
    dob = fields.Date(string="date of birth")
    gender = fields.Selection([('female','Female'),
                                ('male','Male'),
                                ('other','Other')
                                ])
    percentage = fields.Float(string="mark")
    image = fields.Image(string="photo")



    
    
