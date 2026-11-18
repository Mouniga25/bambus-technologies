from odoo import models,fields

class BoardingInfo(models.Model):
    _name='boarding.info'
    _description='Boarding Point'
    
    
    place_id=fields.Many2one('place.info',string="Place Name")
    boarding_name=fields.Char(string="Boarding Point")
  
  
    
   