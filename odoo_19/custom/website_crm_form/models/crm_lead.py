from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    enquiry_number = fields.Char(
        string='Enquiry Number',
        readonly=True,
        copy=False,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            if not vals.get('enquiry_number'):
                vals['enquiry_number'] = (
                    self.env['ir.sequence'].sudo().next_by_code(
                        'customer.enquiry'
                    ) or 'New'
                )

        return super().create(vals_list)