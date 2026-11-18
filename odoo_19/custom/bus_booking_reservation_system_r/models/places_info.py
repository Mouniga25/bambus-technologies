from odoo import models, fields,api

class PlaceDetails(models.Model):
    _name = 'place.info'
    _description = 'Places'
    _rec_name='place_name'
    
    place_name=fields.Char(string="Place Name")
    boarding_point_ids=fields.One2many('boarding.info','place_id',string="Boarding Point")
    booking_count=fields.Integer(compute="_booking_count")
    def _booking_count(self):
        for rec in self:
            rec.booking_count = self.env['booking.info'].search_count([('class_of_service_id', '=', self.id)])
    
    def action_view_bookings(self):
        booking_ids = self.env['booking.info'].search([('class_of_service_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Booking',
            'res_model': 'booking.info',
            'view_mode': 'list',
            'domain' : [('id', '=', booking_ids.ids)]
            
            
        }  