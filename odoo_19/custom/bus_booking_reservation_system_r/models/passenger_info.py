from odoo import models,fields,api
from datetime import date
from odoo.exceptions import ValidationError
class Passengerinfo(models.Model):
    _name='passenger.info.line'
    _description='Passenger '
    _rec_name='passenger_name'
    
    booking_id=fields.Many2one('booking.info')
    passenger_name=fields.Char(string="Name")
    age=fields.Integer(string="Age")
    gender=fields.Selection([('male','Male'),
                             ('female','Female')],string="Gender")
    passenger_type = fields.Selection([('adult','Adult'),
                                       ('child','Child')],string="Passenger Type")
    seat_preference=fields.Selection([('window','Window'),
                                      ('middle','Middle'),
                                      ('aisle','Aisle')],string="Seat Prefrence")
    
    
    

    
    @api.constrains('passenger_name')
    def _check_passenger_name(self):
        for rec in self:
            if not rec.passenger_name.isalpha():
                raise ValidationError(" passenger Name must be contain characters only")
            
            elif self.passenger_name:
                self.duplicate_name_check = self.env['passenger.info.line'].search_count(['passenger_name','=',self.passenger_name])
                raise ValidationError("same passenger should not be allowed twice")
    @api.onchange('age')
    def _onchange_age(self):
        if self.age >= 12:
            self.passenger_type ='adult'
        elif self.age <=12:
            self.passenger_type='child'
            
   
    @api.constrains('passenger_name')
    def _check_passenger_name(self):
        for rec in self:
            if not rec.passenger_name.isalpha():
                raise ValidationError(" passenger Name must be contain characters only")

    @api.onchange('age')
    def _check_age(self):
        for rec in self:
            if rec.age >=120:
                raise ValidationError("Age should not exceed 120.")
            
                

    def action_click(self):
        action_ref = self.env.ref('bus_booking_reservation_system_r.action_popup_information').read()[0]
        return action_ref     
        
    
   
    
        
    