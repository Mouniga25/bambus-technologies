from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SettlementInformation(models.Model):
    _name = 'settlement.information'
    _description = 'Settlement Information'
    _order = 'payment_date desc'

    name = fields.Char(string='Settlement Reference',required=True,copy=False,default='New')
    artisan_id = fields.Many2one('village.artisan',string='Artisan',required=True,ondelete='restrict')
    production_id = fields.Many2one('production.information',string='Production',required=True,ondelete='restrict')
    quantity = fields.Float(string='Quantity',required=True)
    labour_rate = fields.Float(string='Labour Rate',required=True)
    total_amount = fields.Float(string='Total Amount',compute='_compute_total_amount',store=True)
    payment_date = fields.Date(string='Payment Date',required=True,default=fields.Date.today)
    status = fields.Selection([('draft', 'Draft'),('pending', 'Pending'),('paid', 'Paid'),('cancelled', 'Cancelled'),],string='Status',default='draft',required=True)

    @api.onchange('production_id')
    def _onchange_production_id(self):
        for record in self:
            if record.production_id:
                record.artisan_id = record.production_id.artisan_id
                record.quantity = record.production_id.passed_qty

    @api.depends('quantity', 'labour_rate')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = (
                record.quantity * record.labour_rate
            )

    @api.onchange('production_id')
    def _onchange_production_id(self):
        for record in self:
            if record.production_id:
                record.artisan_id = record.production_id.artisan_id
                record.quantity = record.production_id.passed_qty
                record.labour_rate = record.production_id.labour_cost

    @api.constrains('quantity', 'labour_rate')
    def _check_values(self):
        for record in self:

            if record.quantity <= 0:
                raise ValidationError(
                    'Settlement Quantity must be greater than zero.'
                )

            if record.labour_rate < 0:
                raise ValidationError(
                    'Labour Rate cannot be negative.'
                )

    def action_submit(self):
        for record in self:

            if record.status != 'draft':
                raise ValidationError(
                    'Only Draft settlements can be submitted.'
                )

            if not record.production_id:
                raise ValidationError(
                    'Production must be selected.'
                )

            if record.production_id.status != 'completed':
                raise ValidationError(
                    'Settlement can be submitted only for completed production.'
                )

            record.status = 'pending'

    def action_mark_paid(self):
        for record in self:

            if record.status != 'pending':
                raise ValidationError(
                    'Only Pending settlements can be marked as Paid.'
                )

            record.status = 'paid'

    def action_cancel(self):
        for record in self:

            if record.status == 'paid':
                raise ValidationError(
                    'Paid settlement cannot be cancelled.'
                )

            record.status = 'cancelled'

    def action_reset_to_draft(self):
        for record in self:
            record.status = 'draft'