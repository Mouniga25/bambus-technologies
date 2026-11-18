from odoo import api, fields, models

class VehicleInfo(models.Model):
    _name = 'vehicle.info'
    _description = "Vehicle Info"

    # Vehicle Details
    vehicle_name = fields.Char(string="Vehicle Name", required=True)
    vehicle_number =  fields.Char(string="Vehicle Number ", required=True, size= 10)
    vehicle_type = fields.Selection([('car','Car'),
                                    ('bike','Bike'),
                                ('bus','Bus')])
    rent_per_day = fields.Float(string="Rent Per Day",required=True)
    status =  fields.Selection([('available', 'Available'),('booked', 'Booked'),('maintenance', 'Maintenance')], string="Status", default='available')
    available = fields.fields.Boolean(string="Available",compute="_compute_available",store=True)
    company_id =fields.Char(string="Company", required=True)
    sequence_number =fields.Char(string="Sequence Number",readonly=True,copy=False,default="New")