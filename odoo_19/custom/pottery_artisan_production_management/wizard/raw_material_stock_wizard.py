from odoo import models, fields
from odoo.exceptions import ValidationError


class RawMaterialStockWizard(models.TransientModel):
    _name = 'raw.material.stock.wizard'
    _description = 'Raw Material Stock Adjustment Wizard'

    raw_material_id = fields.Many2one(
        'raw.material.information',
        string='Raw Material',
        required=True,
        readonly=True
    )

    current_quantity = fields.Float(
        string='Current Quantity',
        readonly=True
    )

    adjustment_quantity = fields.Float(
        string='Adjustment Quantity',
        required=True
    )

    reason = fields.Char(
        string='Reason',
        required=True
    )

    def action_confirm(self):
        self.ensure_one()

        if self.adjustment_quantity <= 0:
            raise ValidationError(
                'Adjustment Quantity must be greater than zero.'
            )

        self.raw_material_id.available_quantity += self.adjustment_quantity

        return {
            'type': 'ir.actions.act_window_close'
        }
    