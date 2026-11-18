from odoo import api, fields, models
from datetime import date
from odoo.exceptions import ValidationError

class ClassOfService(models.Model):
    _name = 'classof.service'
    _description = "Class Of Service"
    _rec_name ="service_name"



    service_name = fields.Selection([('all_classes',' ALL CLASSES'),
                                ('ac_sleeper','AC SLEEPER'),
                                ('ac_sleeper_seater','AC SLEEPER SEATER'),
                                ('non_ac_sleeper','NON AC SLEEPER'),
                                ('non_ac_sleeper_seater','NON AC SLEEPER SEATER'),
                                ('deluxe','DELUXE'),
                                ('ultra_deluxe','ULTRA DELUXE')
                                ])
    price_of_service = fields.Integer(string="Price of Service")
    number_of_seats = fields.Integer(string="Number of Seats")


    @api.onchange("price_of_service")
    def onchange_age(self):
        if self.price_of_service and self.price_of_service <= 0 :
            raise ValidationError("Price of service greater than 0")
