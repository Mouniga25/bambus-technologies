from odoo import fields, models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    vdi_generated = fields.Boolean(
        string="VDI Generated",
        default=False,
        index=True,
    )

    def action_feedback(self, feedback=False, attachment_ids=None):
        vdi_activities = self.filtered(
            lambda activity: (
                activity.vdi_generated
                and activity.res_model == "purchase.order"
                and activity.res_id
            ),
        )

        result = super().action_feedback(
            feedback=feedback,
            attachment_ids=attachment_ids,
        )

        for activity in vdi_activities:
            order = self.env["purchase.order"].browse(
                activity.res_id,
            ).exists()

            if order:
                order.vdi_acknowledged_level = order.vdi_risk_level

        return result
