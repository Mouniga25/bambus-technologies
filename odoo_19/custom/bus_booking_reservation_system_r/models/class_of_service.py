from odoo import models, fields,api
from odoo.exceptions import ValidationError

class PlaceDetails(models.Model):
    _name = 'service.info'
    _description = 'Places'
    _rec_name='service_name'
    
    service_name = fields.Selection([('ac sleeper','AC SLEEPER'),
                                         ('non ac sleeper','Non Ac Sleeper'),
                                         ('non ac sleeper seater',' Non Ac Sleeper Seater'),
                                         ('deluxe',' Deluxe'),
                                         ('ultra deluxe','Ultra Deluxe')],string='Class Of Service')
    price_of_service= fields.Float( string="Price Of Service")
    number_of_seats = fields.Integer(string="Number of Seats")
    booking_count = fields.Integer(compute="_booking_count")
    state=fields.Selection([('available','Available'),('not_available','Not_Available')],string="Status",default="available")
    
    def _booking_count(self):
        for rec in self:
            rec.booking_count = self.env['booking.info'].search_count([('class_of_service_id', '=', self.id)])
            
    
    
    @api.depends('service_name', 'price_of_service')
    def _compute_display_name(self):
        for record in self:
            if record.service_name and record.price_of_service: 
                record.display_name = f"{record.service_name} - {record.price_of_service}"
            else:
                record.display_name = record.service_name     
                
    def action_view_bookings(self):
        booking_ids = self.env['booking.info'].search([('class_of_service_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Booking',
            'res_model': 'booking.info',
            'view_mode': 'list',
            'domain' : [('id', '=', booking_ids.ids)]
            
            
        }  
    
    @api.onchange('number_of_seats')
    def _onchange_number_of_seats(self):
        for rec in self:
                if rec.number_of_seats <= 0:
                    rec.state = 'not_available'
                else:
                    rec.state = 'available'
            
    #field search
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = [
                '|',
                ('price_of_service', operator, name),
                ('service_name', operator, name),
            ]
        final_domain = args + domain
        partners = self.search(final_domain, limit=limit)
        return [(partner.id, partner.display_name) for partner in partners]


                    
    
    
    
    
