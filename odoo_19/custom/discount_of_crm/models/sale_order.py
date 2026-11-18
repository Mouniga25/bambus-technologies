from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    lead_id = fields.Many2one(
        'crm.lead',
        string="Lead"
    )

    discount = fields.Float(
        string="Discount"
    )
    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        lead = self.env['crm.lead'].browse(
            self.env.context.get('active_id')
        )
        res['lead_id'] = lead.id
        res['discount'] = lead.crm_discount

        return res
    


