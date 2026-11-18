from odoo import models, fields, api

class BookingInfo(models.Model):
    _name = "booking.info"
    _description = "Booking Info"

    booking_number = fields.Char(string="Booking Number",readonly=True,copy=False,default="New")
    customer_id = fields.Many2one("vehicle.customer",string="Customer",required=True)
    vehicle_id = fields.Many2one("vehicle.rental",string="Vehicle",required=True)
    pickup_date = fields.Date(string="Pickup Date",required=True)
    return_date = fields.Date(string="Return Date",required=True)
    no_of_days = fields.Integer(string="No of Days",compute="_compute_no_of_days",store=True)
    rent_per_day = fields.Float(string="Rent Per Day",related="vehicle_id.rent_per_day",store=True,readonly=True)
    total_amount = fields.Float(string="Total Amount",compute="_compute_total_amount",store=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')], string="Status", default="draft")
    accessory_ids = fields.Many2many("vehicle.accessory",string="Accessories")
    payment_line_ids = fields.One2many("vehicle.payment.line","booking_id",string="Payment Lines")