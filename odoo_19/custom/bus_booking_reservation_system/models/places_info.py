from odoo import api, fields, models
from datetime import date

class PlaceInfo(models.Model):
    _name = 'places.info'
    _description = "Place Info"
    _rec_name ="place_name"

    place_name = fields.Char(string="Place Name")
    


    address_lines= fields.One2many(comodel_name="places.info.line", 
                                     inverse_name = 'boarding_point_id')
    



class PlaceInfoLine(models.Model):
    _name = 'places.info.line'
    _description = 'Place Info Line'

    
    boarding_point_id = fields.Many2one(comodel_name='places.info')
    boarding_point = fields.Char(string="Boarding Points")   
