from odoo import fields, models


class PurchaseVendorRiskWarning(models.TransientModel):
    _name = "purchase.vendor.risk.warning"
    _description = "Purchase Vendor Risk Warning"

    purchase_order_id = fields.Many2one(
        "purchase.order",
        string="Purchase Order",
        required=True,
    )
    def action_continue(self):
        self.ensure_one()

        order = self.purchase_order_id

        result = order._vdi_do_confirm()

        return result