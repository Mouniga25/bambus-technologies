from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DeliveryInformation(models.Model):
    _name = 'delivery.information'
    _description = 'Delivery Information'
    _order = 'delivery_date desc'

    name = fields.Char(string='Delivery Reference',required=True,copy=False,default='New')
    order_id = fields.Many2one('customer.order.information',string='Customer Order',required=True,ondelete='restrict')
    customer_id = fields.Many2one('res.partner',string='Customer',related='order_id.customer_id',store=True,readonly=True)
    delivery_date = fields.Date(string='Delivery Date',required=True,default=fields.Date.today)
    quantity = fields.Float(string='Delivery Quantity',required=True)
    vehicle_number = fields.Char(string='Vehicle Number',required=True)
    status = fields.Selection([('draft', 'Draft'),('ready', 'Ready'),('in_transit', 'In Transit'),('delivered', 'Delivered'),('cancelled', 'Cancelled'),],string='Status',default='draft',required=True)
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.company,required=True)


    # -----------------SEQUENCE------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code(
                        'delivery.information'
                    ) or 'New'
                )
        return super().create(vals_list)

#########
# compute fields
#########


#########
# Onchange
#########
    @api.onchange('order_id')
    def _onchange_order_id(self):
        for record in self:
            if not record.order_id:
                record.customer_id = False
                record.quantity = 0.0
                return
            record.customer_id = record.order_id.customer_id
            productions = record.order_id.production_ids.filtered(lambda p: p.status == 'completed')
            available_qty = sum(productions.mapped('final_good_qty'))
            record.quantity = available_qty

#########
# Constrains
#########
    @api.constrains('quantity', 'order_id')
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError('Delivery Quantity must be greater than zero.')
            if not record.order_id:
                continue
            order_qty = record.order_id.total_quantity
            delivered_qty = sum(
                record.order_id.delivery_ids
                .filtered(lambda d: d.status != 'cancelled' and d.id != record.id)
                .mapped('quantity')
            )
            available_qty = order_qty - delivered_qty
            if record.quantity > available_qty:
                raise ValidationError(
                    f'Delivery Quantity ({record.quantity}) cannot exceed '
                    f'available order quantity ({available_qty}).'
                )

#########
# Button
#########
    #=--------------------- DELIVERY READY-----------------
    def action_mark_ready(self):
        for record in self:
            if record.status != 'draft':
                raise ValidationError('Only Draft deliveries can be marked as Ready.')
            if record.order_id.status != 'confirmed':
                raise ValidationError('Only confirmed orders can be delivered.')
            if not record.customer_id.email:
                raise ValidationError('Customer email is not available.')
            if not record.company_id.email:
                raise ValidationError('Company email is not configured.')
            record.status = 'ready'
            template = self.env.ref('pottery_artisan_production_management.mail_template_delivery_ready')
            template.send_mail(
                record.id,
                force_send=True,
                email_values={
                    'email_from': record.company_id.email,
                    'email_to': record.customer_id.email,
                    'reply_to': record.company_id.email,
                    'subject': (
                        f'Your Order {record.order_id.name} '
                        f'is Ready for Delivery'
                    ),
                }
            )
            productions = self.env['production.information'].search([('customer_order_id', '=', record.order_id.id),('status', '=', 'completed'),])
            final_good_qty = sum(productions.mapped('final_good_qty'))
            if final_good_qty < record.quantity:
                raise ValidationError(
                    f'Insufficient finished quantity. '
                    f'Available: {final_good_qty}, '
                    f'Required for delivery: {record.quantity}.'
                )

    #------------START DELIVERY-----------------------
    def action_start_delivery(self):
        for record in self:
            if record.status != 'ready':
                raise ValidationError('Delivery must be Ready before starting transit.')
            if not record.customer_id.email:
                raise ValidationError('Customer email is not available.')
            company_email = record.company_id.email or self.env.company.email
            if not company_email:
                raise ValidationError('Company email is not configured.')
            record.status = 'in_transit'
            template = self.env.ref(
                'pottery_artisan_production_management.mail_template_delivery_in_transit'
            )
            template.send_mail(
                record.id,
                force_send=True,
                email_values={
                    'email_from': company_email,
                    'email_to': record.customer_id.email,
                    'reply_to': company_email,
                    'subject': (
                        f'Your Order {record.order_id.name} '
                        f'is On the Way'
                    ),
                }
            )

    # -----------------MARK DELIVERED-------------------------
    def action_mark_delivered(self):
        for record in self:
        # ---------CHECK DELIVERY STATUS-----------
            if record.status != 'in_transit':
                raise ValidationError('Delivery must be In Transit before marking Delivered.')
            # -------CHECK CUSTOMER PAYMENT-------
            if record.order_id.payment_status != 'paid':
                raise ValidationError(
                    'Customer payment must be completed before marking '
                'the delivery as Delivered.'
                )
        # ------CHECK PRODUCTION SETTLEMENT-------
            productions = self.env['production.information'].search([('customer_order_id', '=', record.order_id.id),('status', '=', 'completed'),])
            settlement = self.env['settlement.information'].search([('production_id', 'in', productions.ids),('status', '=', 'paid'),], limit=1)
            if not settlement:
                unpaid_settlement = self.env['settlement.information'].search([('production_id', 'in', productions.ids),('status', '!=', 'paid'),], limit=1)
                if unpaid_settlement:
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Settlement',
                        'res_model': 'settlement.information',
                        'view_mode': 'form',
                        'res_id': unpaid_settlement.id,
                        'target': 'current',
                    }

        # -------CHECK EMAIL------
            if not record.customer_id.email:
                raise ValidationError('Customer email is not available.')
            if not record.company_id.email:
                raise ValidationError('Company email is not configured.')
        # ------MARK DELIVERED------
            record.status = 'delivered'
            record.order_id.status = 'delivered'

        # --------SEND DELIVERY EMAIL-------
            template = self.env.ref('pottery_artisan_production_management.mail_template_delivery_delivered')
            template.send_mail(
                record.id,
                force_send=True,
                email_values={
                    'email_from': record.company_id.email,
                    'email_to': record.customer_id.email,
                    'reply_to': record.company_id.email,
                    'subject': (
                        f'Your Order {record.order_id.name} '
                        f'Has Been Delivered'
                    ),
                }
            )
    # -------CANCEL DELIVERY-------
    def action_cancel(self):
        for record in self:
            if record.status == 'delivered':
                raise ValidationError('Delivered delivery cannot be cancelled.')
            record.status = 'cancelled'

    # RESET TO DRAFT
    def action_reset_to_draft(self):
        for record in self:
            record.status = 'draft'