from odoo import models, fields, api
from odoo.exceptions import ValidationError


class QualityInformation(models.Model):
    _name = 'quality.information'
    _description = 'Quality Information'
    _order = 'check_date desc'

    name = fields.Char(string='Quality Reference',required=True,copy=False,default='New')
    production_id = fields.Many2one('production.information',string='Production',required=True,ondelete='restrict')
    inspector = fields.Many2one('res.users',string='Inspector',required=True)
    check_date = fields.Date(string='Check Date',required=True,default=fields.Date.today)
    produced_qty = fields.Float(string='Produced Quantity',related='production_id.produced_qty',store=True,)
    passed_qty = fields.Float(string='Passed Quantity',required=True,default=0.0)
    rejected_qty = fields.Float(string='Rejected Quantity',required=True,default=0.0)
    remarks = fields.Text(string='Remarks')
    status = fields.Selection([('pending', 'Pending'),('approved', 'Approved'),('rejected', 'Rejected'),],string='Status',default='pending',required=True)
    product_id = fields.Many2one(related='production_id.product_id',string='Product',readonly=True,store=True)
    # =========================================================
    # SEQUENCE
    # =========================================================

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            if vals.get('name', 'New') == 'New':

                vals['name'] = (
                    self.env['ir.sequence'].next_by_code(
                        'quality.information'
                    ) or 'New'
                )

        return super().create(vals_list)

    # =========================================================
    # VALIDATION
    # =========================================================

    @api.constrains(
        'produced_qty',
        'passed_qty',
        'rejected_qty'
    )
    def _check_quality_quantities(self):

        for record in self:

            if record.produced_qty < 0:

                raise ValidationError(
                    'Produced Quantity cannot be negative.'
                )

            if record.passed_qty < 0:

                raise ValidationError(
                    'Passed Quantity cannot be negative.'
                )

            if record.rejected_qty < 0:

                raise ValidationError(
                    'Rejected Quantity cannot be negative.'
                )

            total_quantity = (
                record.passed_qty +
                record.rejected_qty
            )

            if total_quantity > record.produced_qty:

                raise ValidationError(
                    'Passed Quantity + Rejected Quantity '
                    'cannot be greater than Produced Quantity.'
                )

    # =========================================================
    # APPROVE
    # =========================================================

    def action_approve(self):
        for record in self:
            if record.status != 'pending':
                continue

            # Quantity validation
            if (record.passed_qty + record.rejected_qty) > record.produced_qty:
                raise ValidationError('Passed Quantity + Rejected Quantity ''cannot be greater than Produced Quantity.')
            if record.passed_qty <= 0:
                raise ValidationError('Passed Quantity must be greater than zero ''before approving the Quality Check.')
            # Approve Quality Check
            record.status = 'approved'
            # Update Production
            production = record.production_id
            production.produced_qty = record.produced_qty
            production.rejected_qty = record.rejected_qty
            # Check recovery requirement
            if production.customer_order_id:
                order_qty = sum(production.customer_order_id.order_line_lines.mapped('quantity'))
                pending_qty = order_qty - record.passed_qty
                if pending_qty > 0:
                    production.recovery_required = True
                    production.pending_quantity = pending_qty
                    production.recovery_quantity = pending_qty
                    production.recovery_status = 'pending'
                else:
                    production.recovery_required = False
                    production.pending_quantity = 0.0
                    production.recovery_quantity = 0.0
                    production.recovery_status = 'not_required'
    # =========================================================
    # REJECT
    # =========================================================

    def action_reject(self):

        for record in self:

            if record.status != 'pending':
                continue

            if not record.remarks:

                raise ValidationError(
                    'Please enter Remarks before rejecting '
                    'the Quality Check.'
                )

            record.status = 'rejected'

    # =========================================================
    # RESET TO PENDING
    # =========================================================

    def action_reset_pending(self):

        for record in self:

            record.status = 'pending'

    # =========================================================
    # WRITE VALIDATION
    # =========================================================

    def write(self, vals):

        for record in self:

            if record.status in [
                'approved',
                'rejected'
            ]:

                allowed_fields = {
                    'status',
                    'remarks'
                }

                if set(vals.keys()) - allowed_fields:

                    raise ValidationError(
                        'Approved or Rejected Quality Check '
                        'cannot be modified.'
                    )

        return super().write(vals)

    # =========================================================
    # DELETE VALIDATION
    # =========================================================

    def unlink(self):

        for record in self:

            if record.status in [
                'approved',
                'rejected'
            ]:

                raise ValidationError(
                    'Approved or Rejected Quality Check '
                    'cannot be deleted.'
                )

        return super().unlink()