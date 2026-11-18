from odoo import models, fields
from odoo.exceptions import ValidationError


class CustomerOrderProductionWizard(models.TransientModel):
    _name = 'customer.order.production.wizard'
    _description = 'Create Production from Customer Order'

    order_id = fields.Many2one(
        'customer.order.information',
        string='Customer Order',
        required=True,
        readonly=True
    )

    order_line_id = fields.Many2one(
        'customer.order.line',
        string='Order Line',
        required=True,
        readonly=True
    )

    product_id = fields.Many2one(
        'pottery.product.information',
        string='Product',
        related='order_line_id.product_id',
        readonly=True
    )

    quantity = fields.Float(
        string='Quantity',
        related='order_line_id.quantity',
        readonly=True
    )

    artisan_id = fields.Many2one(
        'village.artisan',
        string='Artisan',
        required=True,
        domain=[('active', '=', True)]
    )

    def action_create_production(self):
        self.ensure_one()

        if self.order_id.status != 'confirmed':
            raise ValidationError(
                'Only Confirmed orders can create production.'
            )

        if not self.order_line_id:
            raise ValidationError(
                'Please select an Order Line.'
            )

        if not self.artisan_id:
            raise ValidationError(
                'Please select an Artisan.'
            )

        production = self.env['production.information'].create({
            'customer_order_id': self.order_id.id,
            'product_id': self.product_id.id,
            'quantity': self.quantity,
            'artisan_id': self.artisan_id.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Production',
            'res_model': 'production.information',
            'view_mode': 'form',
            'res_id': production.id,
            'target': 'current',
        }