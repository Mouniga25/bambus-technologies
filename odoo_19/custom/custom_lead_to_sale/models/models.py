from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"
    _rec_name = "crm_discount"

    lead_id = fields.Many2one(
        "crm.lead",
        string="Discount"
    )

