from odoo import fields, models


class FleetServiceType(models.Model):
    _inherit = "fleet.service.type"

    cost_classification = fields.Selection([
            ("preventive", "Preventive Maintenance"),
            ("corrective", "Corrective Maintenance"),
            ("major", "Major Repair"),
            ("accident", "Accident Repair"),
            ("inspection", "Inspection"),
            ("other", "Other"),
        ],string="Cost Classification",default="other",)
    consider_for_replacement = fields.Boolean(string="Consider for Replacement Analysis",default=False,)