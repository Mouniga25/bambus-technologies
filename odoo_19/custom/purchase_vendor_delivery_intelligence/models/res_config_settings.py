from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    vdi_history_days = fields.Integer(related="company_id.vdi_history_days", readonly=False)
    vdi_min_sample_lines = fields.Integer(related="company_id.vdi_min_sample_lines", readonly=False)
    vdi_grace_days = fields.Integer(related="company_id.vdi_grace_days", readonly=False)
    vdi_due_soon_days = fields.Integer(related="company_id.vdi_due_soon_days", readonly=False)
    vdi_reliable_score = fields.Float(related="company_id.vdi_reliable_score", readonly=False)
    vdi_watch_score = fields.Float(related="company_id.vdi_watch_score", readonly=False)
    vdi_enable_activities = fields.Boolean(related="company_id.vdi_enable_activities", readonly=False)
    vdi_fallback_buyer_id = fields.Many2one(related="company_id.vdi_fallback_buyer_id", readonly=False)
