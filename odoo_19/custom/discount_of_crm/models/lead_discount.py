from odoo import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    crm_discount = fields.Float(
        string="Discount"
    )



    