from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DeliveryCreationWizard(models.TransientModel):
    _name = 'delivery.creation.wizard'
    _description = 'Delivery Creation Wizard'

    production_id = fields.Many2one(
        'production.information',
        string='Production',
        required=True,
        readonly=True
    )

    order_id = fields.Many2one(
        'customer.order.information',
        string='Customer Order',
        related='production_id.customer_order_id',
        readonly=True
    )

    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related='order_id.customer_id',
        readonly=True
    )

    quantity = fields.Float(
        string='Delivery Quantity',
        required=True,
        readonly=True
    )

    delivery_date = fields.Date(
        string='Delivery Date',
        required=True,
        default=fields.Date.today
    )

    vehicle_number = fields.Char(
        string='Vehicle Number',
        required=True
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        production_id = self.env.context.get('default_production_id')

        if production_id:
            production = self.env[
                'production.information'
            ].browse(production_id)

            res['production_id'] = production.id
            res['quantity'] = production.final_good_qty

        return res

    def action_create_delivery(self):
        self.ensure_one()
        if not self.production_id:
            raise ValidationError('Production is required.')
        if self.production_id.status != 'completed':
            raise ValidationError('Production must be completed before creating delivery.')
        if not self.order_id:
            raise ValidationError('Customer Order is not linked with this production.')
        if self.quantity <= 0:
            raise ValidationError('Delivery Quantity must be greater than zero.')
        if not self.vehicle_number:
            raise ValidationError('Vehicle Number is required.')
        delivery = self.env['delivery.information'].create({
            'order_id': self.order_id.id,
            'quantity': self.quantity,
            'delivery_date': self.delivery_date,
            'vehicle_number': self.vehicle_number,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Delivery',
            'res_model': 'delivery.information',
            'view_mode': 'form',
            'res_id': delivery.id,
            'target': 'current',
        }