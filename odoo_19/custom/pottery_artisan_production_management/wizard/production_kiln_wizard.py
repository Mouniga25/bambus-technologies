from odoo import models, fields


class ProductionKilnWizard(models.TransientModel):
    _name = 'production.kiln.wizard'
    _description = 'Production Kiln Assignment Wizard'

    kiln_id = fields.Many2one('kiln.information',string='Kiln',required=True)
    
    def action_assign_kiln(self):
        production_ids = self.env.context.get('active_ids', [])
        productions = self.env['production.information'].browse(production_ids)
        productions.write({'kiln_id': self.kiln_id.id})

        return {'type': 'ir.actions.act_window_close'}