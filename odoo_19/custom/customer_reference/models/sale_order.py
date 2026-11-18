from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    
    date_of_birth = fields.Date(string="Date Of Birth")
    age = fields.Integer(string="Age", compute='_compute_age',store=True)



    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth:
                today = date.today()
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 0


    def action_confirm(self):
        print("-------custom function-----------")
        for rec in self:
            if rec.age < 18:
                raise ValidationError("age must have above 18")
            
        return super().action_confirm()


    

