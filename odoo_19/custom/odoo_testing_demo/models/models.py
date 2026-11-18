from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TestStudent(models.Model):
    _name = 'test.student'
    _description = 'Test Student'

    name = fields.Char(string='Name', required=True)
    age = fields.Integer(string='Age')
    email = fields.Char(string='Email')
    double_age = fields.Integer(compute='_compute_double_age')

    @api.constrains('age')
    def _check_age(self):
        for student in self:
            if student.age < 0:
                raise ValidationError("Age cannot be negative.")

    @api.depends('age')
    def _compute_double_age(self):
        for student in self:
            student.double_age = student.age * 2

    @api.onchange('age')
    def _onchange_age(self):
        if self.age >= 18:
            self.email = 'adult@example.com' 

    def action_pass(self):
        for student in self:
            student.email = 'passed@example.com' 

    