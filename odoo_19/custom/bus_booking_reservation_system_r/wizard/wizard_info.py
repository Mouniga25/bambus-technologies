from odoo import models, fields,api

class PoppupInformation(models.TransientModel):
    _name = 'popup.information'
    _description = 'Popup Information'

    name = fields.Char()
   
    age=fields.Integer(string="Age")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ]) 
    passenger_type = fields.Selection([('adult','Adult'),
                                       ('child','Child')],string="Passenger Type")
    seat_preference=fields.Selection([('window','Window'),
                                      ('middle','Middle'),
                                      ('aisle','Aisle')])

    @api.model
    def default_get(self, fields_list):
        res = {}
        passenger = self.env['passenger.info.line'].browse(
            self.env.context.get('active_id')
        )

        res.update({'name': passenger.passenger_name,
                    'age':passenger.age,
                    'gender': passenger.gender,
                    'seat_preference':passenger.seat_preference,
                    'passenger_type':passenger.passenger_type})
        return res
    
    def action_save(self):
        active_id=self.env.context.get('active_id')
        if active_id:
            passenger_record= self.env['passenger.info.line'].browse(active_id)
            
            passenger_record.update({'passenger_name':self.name,
                                     'age':self.age,
                                     'gender':self.gender,
                                     'seat_preference':self.seat_preference,
                                     'passenger_type' : self.passenger_type})
            return passenger_record
            
            
        
