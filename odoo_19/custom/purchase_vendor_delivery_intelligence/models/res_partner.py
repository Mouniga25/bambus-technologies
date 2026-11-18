from datetime import timedelta

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    vdi_vendor_score = fields.Float(string="Vendor Delivery Score", compute="_compute_vdi_vendor_intelligence")
    vdi_vendor_grade = fields.Selection(selection=[
        ("insufficient", "Insufficient History"),
        ("reliable", "Reliable"),
        ("watchlist", "Watchlist"),
        ("high_risk", "High Risk")], string="Vendor Grade", compute="_compute_vdi_vendor_intelligence")
    vdi_eligible_line_count = fields.Integer(string="Eligible Lines", compute="_compute_vdi_vendor_intelligence")
    vdi_on_time_mean = fields.Float(string="Mean On-Time %", compute="_compute_vdi_vendor_intelligence")
    vdi_fill_mean = fields.Float(string="Mean Fill %", compute="_compute_vdi_vendor_intelligence")
    vdi_delay_mean = fields.Float(string="Mean Delay Days", compute="_compute_vdi_vendor_intelligence")
    vdi_analysis_start = fields.Date(string="Analysis Start", compute="_compute_vdi_vendor_intelligence")
    vdi_analysis_end = fields.Date(string="Analysis End", compute="_compute_vdi_vendor_intelligence")
    vdi_last_analysis_at = fields.Datetime(string="Latest Analysis", compute="_compute_vdi_vendor_intelligence")
    vdi_insufficient_reason = fields.Text(string="Insufficient History Reason", compute="_compute_vdi_vendor_intelligence")

    @api.depends("company_id","commercial_partner_id",)
    def _compute_vdi_vendor_intelligence(self):
        PurchaseLine = self.env["purchase.order.line"]
        for partner in self:
            partner.vdi_vendor_score = 0.0
            partner.vdi_vendor_grade = "insufficient"
            partner.vdi_eligible_line_count = 0
            partner.vdi_on_time_mean = 0.0
            partner.vdi_fill_mean = 0.0
            partner.vdi_delay_mean = 0.0

            partner.vdi_analysis_start = False
            partner.vdi_analysis_end = False
            partner.vdi_last_analysis_at = False
            partner.vdi_insufficient_reason = False

            company = partner.company_id or self.env.company
            commercial_partner = partner.commercial_partner_id
            today = fields.Date.context_today(partner)
            partner.vdi_analysis_end = today
            partner.vdi_analysis_start = (
                today - timedelta(days=company.vdi_history_days)
            )

            lines = PurchaseLine.search([
                ("order_id.partner_id", "=", commercial_partner.id),
                ("order_id.company_id", "=", company.id),
                ("vdi_sample_eligible", "=", True),
            ])
            evaluated_orders = lines.mapped("order_id").filtered(
                lambda order: order.vdi_last_evaluated_at)
            if evaluated_orders:
                partner.vdi_last_analysis_at = max(
                    evaluated_orders.mapped("vdi_last_evaluated_at"))

            count = len(lines)

            if not count:
                continue

            on_time_mean = sum(
                lines.mapped("vdi_on_time_pct"),
            ) / count

            fill_mean = sum(
                lines.mapped("vdi_fill_pct"),
            ) / count

            delay_lines = lines.filtered(
                lambda line: line.vdi_net_received_qty > 0,
            )

            delay_mean = (
                sum(delay_lines.mapped("vdi_mean_delay_days"))
                / len(delay_lines)
                if delay_lines
                else 0.0
            )

            score = round(
                (0.70 * on_time_mean) +
                (0.30 * fill_mean),
                1,
            )

            min_samples = company.vdi_min_sample_lines
            reliable_score = company.vdi_reliable_score
            watch_score = company.vdi_watch_score
            if count < min_samples:
                partner.vdi_insufficient_reason = (
                    f"Only {count} eligible sample line(s) found. "
                    f"Minimum required is {min_samples}.")
            else:
                partner.vdi_insufficient_reason = False

            if count < min_samples:
                grade = "insufficient"
            elif score >= reliable_score:
                grade = "reliable"
            elif score >= watch_score:
                grade = "watchlist"
            else:
                grade = "high_risk"

            partner.vdi_vendor_score = score
            partner.vdi_vendor_grade = grade
            partner.vdi_eligible_line_count = count
            partner.vdi_on_time_mean = on_time_mean
            partner.vdi_fill_mean = fill_mean
            partner.vdi_delay_mean = delay_mean

    def action_vdi_evaluated_lines(self):
        self.ensure_one()

        company = self.company_id or self.env.company

        return {
            "type": "ir.actions.act_window",
            "name": "Evaluated Lines",
            "res_model": "purchase.order.line",
            "view_mode": "list,form",
            "domain": [
                ("order_id.partner_id", "=", self.commercial_partner_id.id),
                ("order_id.company_id", "=", company.id),
                ("vdi_sample_eligible", "=", True),
            ],
        }
