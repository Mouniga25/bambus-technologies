from datetime import timedelta
import logging
from odoo import _, api, fields, models
_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    vdi_last_evaluated_at = fields.Datetime(string="Last Evaluated At", readonly=True)
    vdi_vendor_score_at_confirmation = fields.Float(string="Vendor Score at Confirmation", readonly=True,)
    
    vdi_last_notified_level = fields.Selection(
        selection=[
            ("not_applicable", "Not Applicable"),
            ("data_gap", "Data Gap"),
            ("complete", "Complete"),
            ("critical", "Critical"),
            ("at_risk", "At Risk"),
            ("due_soon", "Due Soon"),
            ("on_track", "On Track"),
        ], string="Last Notified Risk Level", readonly=True)

    vdi_acknowledged_level = fields.Selection(
        selection=[
            ("not_applicable", "Not Applicable"),
            ("data_gap", "Data Gap"),
            ("complete", "Complete"),
            ("critical", "Critical"),
            ("at_risk", "At Risk"),
            ("due_soon", "Due Soon"),
            ("on_track", "On Track"),
        ], string="Acknowledged Risk Level", readonly=True)

    vdi_risk_level = fields.Selection(selection=[
        ("not_applicable", "Not Applicable"),
        ("data_gap", "Data Gap"),
        ("complete", "Complete"),
        ("critical", "Critical"),
        ("at_risk", "At Risk"),
        ("due_soon", "Due Soon"),
        ("on_track", "On Track")], string="VDI Risk Level", readonly=True)
    vdi_risk_reason = fields.Text(string="VDI Risk Reason", readonly=True)
    vdi_critical_line_count = fields.Integer(string="Critical Lines", readonly=True)
    vdi_at_risk_line_count = fields.Integer(string="At Risk Lines", readonly=True)
    vdi_due_soon_count = fields.Integer(string="Due Soon Lines", readonly=True)
    vdi_open_line_count = fields.Integer(string="Open Lines", readonly=True)
    vdi_earliest_risk_deadline = fields.Datetime(string="Earliest Risk Deadline", readonly=True)
    vdi_eta_extended = fields.Boolean(string="ETA Extended", readonly=True, index=True)
    vdi_supplier_high_risk = fields.Boolean(string="Supplier High Risk", readonly=True, index=True)
    vdi_critical_since = fields.Datetime(string="Critical Since", readonly=True, index=True)
    vdi_critical_over_7_days = fields.Boolean(string="Critical for More Than 7 Days", readonly=True, index=True)

# Risk Change & Trend Intelligence

    vdi_previous_risk_level = fields.Selection(
        selection=[
            ("not_applicable", "Not Applicable"),
            ("data_gap", "Data Gap"),
            ("complete", "Complete"),
            ("on_track", "On Track"),
            ("due_soon", "Due Soon"),
            ("at_risk", "At Risk"),
            ("critical", "Critical"),
        ],
        string="Previous Risk Level",
        readonly=True,
        copy=False,
    )

    vdi_risk_trend = fields.Selection(
        selection=[
            ("improving", "Improving"),
            ("stable", "Stable"),
            ("worsening", "Worsening"),
        ],
        string="Risk Trend",
        default="stable",
        readonly=True,
        copy=False,
    )

    vdi_risk_level_since = fields.Datetime(
        string="Current Risk Since",
        readonly=True,
        copy=False,
    )

    vdi_risk_change_at = fields.Datetime(
        string="Last Risk Change",
        readonly=True,
        copy=False,
    )

    vdi_risk_change_reason = fields.Text(
        string="Risk Change Reason",
        readonly=True,
        copy=False,
    )

    vdi_recovery_status = fields.Selection(
        selection=[
            ("no_action", "No Action"),
            ("action_required", "Action Required"),
            ("monitoring", "Monitoring"),
            ("recovered", "Recovered"),
        ],
        string="Recovery Status",
        default="no_action",
        copy=False,
    )



    @api.onchange("partner_id")
    def _onchange_vdi_vendor_warning(self):
        if not self.partner_id:
            return
        vendor = self.partner_id.commercial_partner_id
        if vendor.vdi_vendor_grade == "high_risk":
            return {
                "warning": {
                    "title": _("High-Risk Vendor Warning"),
                    "message": _(
                        "This vendor has been classified as High Risk."
                    ),
                }
            }
    
    
    def button_confirm(self):
        return self._vdi_do_confirm()

    
    def _vdi_do_confirm(self):
        result = super().button_confirm()
        for order in self:
            order.order_line._vdi_capture_baseline()
            vendor = order.partner_id.commercial_partner_id
            order.vdi_vendor_score_at_confirmation = (vendor.vdi_vendor_score)
        return result

    def button_cancel(self):
        result = super().button_cancel()

        self.action_vdi_refresh()

        return result

    
        # res = super().button_confirm()
        # confirmed = self.filtered(lambda po: po.state in ("purchase", "done"))
        # confirmed.order_line._vdi_capture_baseline()
        # return res

    def _vdi_risk_priority(self, risk_level):
        priorities = {
            "not_applicable": 0,
            "data_gap": 1,
            "complete": 2,
            "on_track": 3,
            "due_soon": 4,
            "at_risk": 5,
            "critical": 6,
        }
        return priorities.get(risk_level, 0)

    def _vdi_get_activity_user(self):
        self.ensure_one()

        return self.user_id or self.company_id.vdi_fallback_buyer_id

    def _vdi_create_risk_activity(self, risk_level):
        self.ensure_one()
        if risk_level not in ("critical", "at_risk", "due_soon"):
             Activity = self.env["mail.activity"]
             existing_activity = Activity.search([
                  ("res_model", "=", "purchase.order"),
                  ("res_id", "=", self.id),
                  ("vdi_generated", "=", True),
                  ("active", "=", True),], limit=1)
             if existing_activity:
                  existing_activity.action_done()
             return

        if not self.company_id.vdi_enable_activities:
            return

        user = self._vdi_get_activity_user()
        if not user:
            return

        Activity = self.env["mail.activity"]
        existing_activity = Activity.search([
            ("res_model", "=", "purchase.order"),
            ("res_id", "=", self.id),
            ("vdi_generated", "=", True),
            ("active", "=", True),
            ], limit=1)

        previous_level = self.vdi_last_notified_level
        if (
            self.vdi_acknowledged_level
            and self.vdi_acknowledged_level == risk_level
        ):
            return

        if existing_activity:
            if (
                previous_level
                and self._vdi_risk_priority(risk_level)
                > self._vdi_risk_priority(previous_level)
            ):
                existing_activity.write({
                    "summary": "VDI Delivery Risk Escalated",
                    "note": (
                        "Purchase Order %s risk has worsened "
                        "from %s to %s."
                    ) % (
                        self.name,
                        previous_level,
                        risk_level,
                    ),
                    "user_id": user.id,
                    "date_deadline": fields.Date.context_today(self),
                })

                self.vdi_last_notified_level = risk_level

            return

        activity_type = self.env.ref(
            "mail.mail_activity_data_todo",
            raise_if_not_found=False,
        )

        if not activity_type:
            return

        Activity.create({
            "activity_type_id": activity_type.id,
            "res_model_id": self.env["ir.model"]._get_id("purchase.order"),
            "res_id": self.id,
            "user_id": user.id,
            "summary": "VDI Delivery Risk Review",
            "note": (
                "Purchase Order %s requires delivery risk attention. "
                "Current risk level: %s."
            ) % (
                self.name,
                dict(
                    self._fields["vdi_risk_level"].selection,
                ).get(risk_level, risk_level),
            ),
            "vdi_generated": True,
            "date_deadline": fields.Date.context_today(self),
        })

        self.vdi_last_notified_level = risk_level

    def _vdi_get_management_summary(self, orders=None):
        """Return company-scoped management summary."""

        self.ensure_one()

        if orders is None:
            orders = self.env["purchase.order"].search([
                ("company_id", "=", self.company_id.id),
                ("state", "in", ("purchase", "done")),
            ])

        company_orders = orders.filtered(
            lambda po: (
                po.company_id == self.company_id
                and po.state in ("purchase", "done")
            ),
        )

        eligible_lines = company_orders.mapped("order_line").filtered(
            lambda line: (
                not line.display_type
                and line.product_id
                and line.product_id.is_storable
                and line.product_qty > 0
            ),
        )

        open_lines = eligible_lines.filtered(
            lambda line: (
                line.vdi_original_qty
                and (
                    line.vdi_original_qty
                    - line.vdi_net_received_qty
                ) > 0
            ),
        )

        open_orders = company_orders.filtered(
            lambda po: any(
                line in open_lines
                for line in po.order_line
            ),
        )

        critical_orders = company_orders.filtered(
            lambda po: po.vdi_risk_level == "critical",
        )

        at_risk_orders = company_orders.filtered(
            lambda po: po.vdi_risk_level == "at_risk",
        )

        due_soon_orders = company_orders.filtered(
            lambda po: po.vdi_risk_level == "due_soon",
        )

        data_quality_lines = eligible_lines.filtered(
            lambda line: bool(line.vdi_data_issue),
        )

        watchlist_suppliers = company_orders.mapped(
            "partner_id.commercial_partner_id",
        ).filtered(
            lambda partner: partner.vdi_vendor_grade == "watchlist",
        )

        outstanding_by_product = {}

        for line in open_lines:
            outstanding_qty = max(
                line.vdi_original_qty
                - line.vdi_net_received_qty,
                0,
            )

            if outstanding_qty <= 0:
                continue

            key = (
                line.product_id.id,
                line.vdi_original_uom_id.id,
            )

            if key not in outstanding_by_product:
                outstanding_by_product[key] = {
                    "product": line.product_id,
                    "uom": line.vdi_original_uom_id,
                    "qty": 0.0,
                }

            outstanding_by_product[key]["qty"] += outstanding_qty

        return {
            "open_pos": len(open_orders),
            "critical_pos": len(critical_orders),
            "at_risk_pos": len(at_risk_orders),
            "due_soon_pos": len(due_soon_orders),
            "unresolved_exposure": len(open_lines),
            "watchlist_suppliers": len(watchlist_suppliers),
            "data_quality_exceptions": len(data_quality_lines),
            "outstanding_by_product": list(
                outstanding_by_product.values(),
            ),
        }

    def action_vdi_refresh(self):
        """Refresh VDI metrics for all selected purchase orders."""
        if not self:
            return

        # Refresh all applicable PO lines in one batch.
        all_lines = self.mapped("order_line").filtered(
            lambda line: not line.display_type,
        )

        if all_lines:
            all_lines._vdi_refresh_metrics()

        now = fields.Datetime.now()

        for order in self:
            lines = order.order_line.filtered(
                lambda line: not line.display_type,
            )
            if order.state == "cancel":
                order.write({
                    "vdi_risk_level": "not_applicable",
                    "vdi_risk_reason": "Purchase order is cancelled.",
                    "vdi_critical_line_count": 0,
                    "vdi_at_risk_line_count": 0,
                    "vdi_due_soon_count": 0,
                    "vdi_open_line_count": 0,
                    "vdi_earliest_risk_deadline": False,
                    "vdi_last_evaluated_at": now,
                    "vdi_eta_extended": False,
                    "vdi_supplier_high_risk": False,
                    "vdi_critical_since": False,
                    "vdi_critical_over_7_days": False,
                    "vdi_acknowledged_level": False,
                    "vdi_last_notified_level": False,
                })

                order._vdi_create_risk_activity("not_applicable")
                continue

            has_eta_extended = any(
                line.vdi_eta_shift_days > 0
                for line in lines
            )

            has_supplier_high_risk = (
                order.partner_id.vdi_vendor_grade == "high_risk"
            )

            risk_lines = lines.filtered(
                lambda line: line.vdi_line_risk_level,
            )

            critical_count = len(
                risk_lines.filtered(
                    lambda line: line.vdi_line_risk_level == "critical",
                ),
            )

            at_risk_count = len(
                risk_lines.filtered(
                    lambda line: line.vdi_line_risk_level == "at_risk",
                ),
            )

            due_soon_count = len(
                risk_lines.filtered(
                    lambda line: line.vdi_line_risk_level == "due_soon",
                ),
            )

            risk_deadlines = risk_lines.filtered(
                lambda line: line.vdi_line_risk_level
                in ("critical", "at_risk", "due_soon"),
            ).mapped("vdi_original_promise")

            earliest_risk_deadline = (
                min(risk_deadlines)
                if risk_deadlines
                else False
            )

            open_lines = risk_lines.filtered(
                lambda line: (
                    line.vdi_original_qty - line.vdi_net_received_qty
                ) > 0,
            )

            if critical_count:
                risk_level = "critical"
                reason = "One or more purchase lines are critical."
            elif at_risk_count:
                risk_level = "at_risk"
                reason = "One or more purchase lines are at risk."
            elif due_soon_count:
                risk_level = "due_soon"
                reason = "One or more purchase lines are due soon."
            elif risk_lines.filtered(
                lambda line: line.vdi_line_risk_level == "data_gap",
            ):
                risk_level = "data_gap"
                reason = (
                    "One or more purchase lines have data quality issues."
                )
            elif not risk_lines:
                risk_level = "not_applicable"
                reason = "No applicable purchase lines."
            elif not open_lines:
                risk_level = "complete"
                reason = "All applicable purchase lines are fully delivered."
            else:
                risk_level = "on_track"
                reason = "No critical, at-risk, or due-soon lines."

            # -------------------------------------------------
            # VDI: RISK CHANGE & TREND INTELLIGENCE
            # -------------------------------------------------

            old_risk = order.vdi_risk_level

            # Higher number means higher delivery risk.
            risk_priority = {
                "not_applicable": 0,
                "data_gap": 1,
                "complete": 2,
                "on_track": 3,
                "due_soon": 4,
                "at_risk": 5,
                "critical": 6,
            }

            old_priority = risk_priority.get(old_risk, 0)
            new_priority = risk_priority.get(risk_level, 0)

            previous_risk = order.vdi_previous_risk_level
            risk_trend = order.vdi_risk_trend or "stable"
            risk_level_since = order.vdi_risk_level_since
            risk_change_at = order.vdi_risk_change_at
            risk_change_reason = order.vdi_risk_change_reason
            recovery_status = order.vdi_recovery_status or "no_action"

            active_risks = ("critical", "at_risk", "due_soon")

            # Initialize current risk start time for existing POs.
            if not risk_level_since:
                risk_level_since = now

            # Check whether the risk level has changed.
            if old_risk and old_risk != risk_level:
                previous_risk = old_risk
                risk_change_at = now
                risk_level_since = now

                risk_change_reason = (
                    f"Risk changed from {old_risk} to {risk_level}. "
                    f"{reason}"
                )

                if new_priority > old_priority:
                    risk_trend = "worsening"
                elif new_priority < old_priority:
                    risk_trend = "improving"
                else:
                    risk_trend = "stable"

                if risk_level in active_risks:
                    if (
                        old_risk not in active_risks
                        or risk_trend == "worsening"
                    ):
                        recovery_status = "action_required"

                elif old_risk in active_risks:
                    recovery_status = "recovered"

            # Existing active-risk PO with no recovery action recorded.
            if (
                risk_level in active_risks
                and recovery_status == "no_action"
            ):
                recovery_status = "action_required"

            if risk_level == "critical":
                critical_since = order.vdi_critical_since or now
                critical_over_7_days = now > (
                    critical_since + timedelta(days=7)
                )
            else:
                critical_since = False
                critical_over_7_days = False

            _logger.info(
                "VDI RECOVERY DEBUG | PO: %s | Risk: %s | Recovery: %s",
                order.name,
                risk_level,
                recovery_status,
            )

            order.write({
                "vdi_risk_level": risk_level,
                "vdi_risk_reason": reason,
                "vdi_critical_line_count": critical_count,
                "vdi_at_risk_line_count": at_risk_count,
                "vdi_due_soon_count": due_soon_count,
                "vdi_open_line_count": len(open_lines),
                "vdi_earliest_risk_deadline": earliest_risk_deadline,
                "vdi_last_evaluated_at": now,
                "vdi_eta_extended": has_eta_extended,
                "vdi_supplier_high_risk": has_supplier_high_risk,
                "vdi_critical_since": critical_since,
                "vdi_critical_over_7_days": critical_over_7_days,
                "vdi_previous_risk_level": previous_risk,
                "vdi_risk_trend": risk_trend,
                "vdi_risk_level_since": risk_level_since,
                "vdi_risk_change_at": risk_change_at,
                "vdi_risk_change_reason": risk_change_reason,
                "vdi_recovery_status": recovery_status,
            })

            if risk_level not in ("critical", "at_risk", "due_soon"):
                order.vdi_acknowledged_level = False
                order.vdi_last_notified_level = False

            # q1 
            _logger.info(
                "VDI SAVED VALUE DEBUG | PO: %s | Recovery: %s",
                order.name,
                order.vdi_recovery_status,
            )


    ########
    # Smart Buttons
    #########

    def action_vdi_risk_lines(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Risk Lines",
            "res_model": "purchase.order.line",
            "view_mode": "list,form",
            "domain": [
                ("order_id", "=", self.id),
                ("vdi_line_risk_level", "in", [
                    "critical",
                    "at_risk",
                    "due_soon",
                    "data_gap",
                ]),
            ],
            "context": {
                "default_order_id": self.id,
            },
        }

    def action_vdi_related_receipts(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Related Receipts",
            "res_model": "stock.picking",
            "view_mode": "list,form",
            "domain": [
                ("purchase_id", "=", self.id),
                ("state", "=", "done"),
                ("picking_type_id.code", "=", "incoming"),
            ],
        }

    # cron
    @api.model
    def _cron_vdi_daily_refresh(self):
        orders = self.search([
            ("company_id", "=", self.env.company.id),
            ("state", "in", ["purchase", "done"]),
        ])

        orders.action_vdi_refresh()

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        result = super().button_validate()

        # Refresh VDI only after the receipt is actually completed.
        done_pickings = self.filtered(
            lambda picking: picking.state == "done"
            and picking.picking_type_code == "incoming"
        )

        if done_pickings:
            purchase_orders = done_pickings.mapped(
                "move_ids.purchase_line_id.order_id"
            )

            if purchase_orders:
                purchase_orders.action_vdi_refresh()

        return result
