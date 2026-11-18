from odoo import fields, models


class SubjectDetails(models.Model):
    _name = 'subject.details'
    _description = 'Subject Details'

    subject_code = fields.Char(string="Subject Code", required=True)
    subject_name = fields.Char(string="Subject Name", required=True)

    semester = fields.Selection([
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
        ('3', 'Semester 3'),
        ('4', 'Semester 4'),
        ('5', 'Semester 5'),
        ('6', 'Semester 6'),
        ('7', 'Semester 7'),
        ('8', 'Semester 8'),
    ], string="Semester", required=True)

    faculty_id = fields.Many2one(
        'faculty.information',
        string="Faculty"
    )

    department_id = fields.Many2one(
        'department.information',
        string="Department"
    )