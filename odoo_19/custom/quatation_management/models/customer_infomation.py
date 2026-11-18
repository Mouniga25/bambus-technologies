from odoo import api, fields, models
from datetime import date
from odoo.exceptions import ValidationError

class CustomerInformation(models.Model):
    _name = 'customer.information'
    _description = 'Customer Information'
    _rec_name = "customer_name"


    customer_name = fields.Char(string="Customer Name")
    order_date = fields.Date(string="Order Date")
    order_lines = fields.One2many(comodel_name="customer.information.line", 
                                  inverse_name='order_id')
    total = fields.Float(string="Total", compute="_compute_total", store=True)

    @api.depends('order_lines.amount')
    def _compute_total(self):
        """
        This function compute total amount
        """
        for record in self:
            total = 0.0
            for line in record.order_lines:
                total += line.amount
                record.total = total



    #create
    @api.model_create_multi
    def create(self, vals):
        if not vals.get('customer_name'):
            raise ValidationError("Name is required")
        return super().create(vals)
    
 

class CustomerInformationLine(models.Model):
    _name = 'customer.information.line'
    _description = 'Customer Information Line'

    order_id = fields.Many2one(comodel_name='customer.information')

    product = fields.Char(string="Product Name")
    quantity = fields.Float(string="Quantity")
    unit_price = fields.Float(string='unit_price')
    amount = fields.Float(string="Amount",compute="_compute_amount",store=True)


    @api.depends('quantity', 'unit_price')
    def _compute_amount(self):
        """
        This function compute amount.
        """
        for rec in self:
            rec.amount = rec.quantity * rec.unit_price
    

    

