from datetime import timedelta
from unittest import result

from odoo import Command, fields
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMetrics(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Vendor M"})
        cls.product = cls.env["product.product"].create(
            {"name": "Widget M", "is_storable": True},
        )

    def _po(self, qty=100, days_ago=10):
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    (0, 0, {
                        "product_id": self.product.id,
                        "product_qty": qty,
                        "price_unit": 1.0,
                        "date_planned": fields.Datetime.now() - timedelta(days=days_ago),
                    }),
                ],
            },
        )
        po.button_confirm()
        return po

    def _receive(self, po, qty, backorder=True):
        picking = po.picking_ids.filtered(lambda p: p.state != "done")[:1]
        picking.move_ids.quantity = qty
        picking.with_context(skip_backorder=True).button_validate()
        return picking

    def _receive_with_backorder(self, po, qty):
        picking = po.picking_ids.filtered(
            lambda p: p.state not in ("done", "cancel")
        )[:1]

        picking.move_ids.quantity = qty

        result = picking.button_validate()

        if (
            isinstance(result, dict)
            and result.get("res_model") == "stock.backorder.confirmation"
        ):
            wizard = self.env["stock.backorder.confirmation"].with_context(
                result.get("context", {})
            ).create({
                "pick_ids": [(6, 0, picking.ids)],
            })

            wizard.process()

        backorder = po.picking_ids.filtered(
            lambda p: p.id != picking.id
            and p.state not in ("done", "cancel")
        )[:1]

        print("T14 PICKING ID:", picking.id)
        print("T14 BACKORDER ID:", backorder.id if backorder else False)

        return picking, backorder

    def _set_done_date(self, picking, days_ago):
        picking.date_done = fields.Datetime.now() - timedelta(days=days_ago)

    def test_split_receipt_60_on_time_40_late(self):  # T03
        po = self._po(100, days_ago=10)  # deadline = 10 days ago + 2 grace
        p1 = self._receive(po, 60)
        self._set_done_date(p1, 9)  # within grace
        p2 = self._receive(po, 40)
        self._set_done_date(p2, 1)  # late
        line = po.order_line
        line._vdi_refresh_metrics()
        self.assertAlmostEqual(line.vdi_on_time_pct, 60.0, places=1)
        self.assertAlmostEqual(line.vdi_fill_pct, 100.0, places=1)
        self.assertGreater(line.vdi_mean_delay_days, 0)

    def test_short_delivery_85_of_100(self):  # T04
        po = self._po(100, days_ago=10)
        p1 = self._receive(po, 85)
        self._set_done_date(p1, 9)
        line = po.order_line
        line._vdi_refresh_metrics()
        self.assertAlmostEqual(line.vdi_fill_pct, 85.0, places=1)

    def test_no_baseline_is_data_gap(self):  # T23
        po = self._po(10)
        line = po.order_line
        line.with_context(vdi_baseline_capture=True).write(
            {"vdi_original_promise": False},
        )
        line._vdi_refresh_metrics()
        self.assertTrue(line.vdi_data_issue)
        self.assertEqual(line.vdi_fill_pct, 0.0)


    def test_four_sample_lines_are_insufficient_history(self):  # T09
        orders = []

        for index in range(4):
            po = self._po(
                qty=100,
                days_ago=10 + index,
            )
            receipt = self._receive(po, 100)
            self._set_done_date(receipt, 7)

            orders.append(po)

        lines = self.env["purchase.order.line"].concat(
            *(po.order_line for po in orders),
        )

        lines._vdi_refresh_metrics()
        orders[0].partner_id._compute_vdi_vendor_intelligence()

        vendor = orders[0].partner_id

        self.assertEqual(
            vendor.vdi_eligible_line_count,
            4,
        )

        self.assertEqual(
            vendor.vdi_vendor_grade,
            "insufficient",
        )

        self.assertIn(
            "Only 4 eligible sample line(s) found",
            vendor.vdi_insufficient_reason,
        )

        self.assertIn(
            "Minimum required is 5",
            vendor.vdi_insufficient_reason,
        )


    def test_open_balance_past_grace_is_critical(self):  # T11
        po = self._po(
            qty=100,
            days_ago=10,
        )

        # Receive only part of the quantity.
        # Remaining 40 units stay open.
        picking, backorder = self._receive_with_backorder(
            po,
            60,
        )

        # Receipt is completed before the deadline.
        self._set_done_date(picking, 12)

        po.order_line._vdi_refresh_metrics()

        line = po.order_line

        print("T11 OPEN QTY:", line.vdi_original_qty - line.vdi_net_received_qty)
        print("T11 RISK:", line.vdi_line_risk_level)
        print("T11 DATA ISSUE:", line.vdi_data_issue)

        self.assertGreater(
            line.vdi_original_qty - line.vdi_net_received_qty,
            0,
        )

        self.assertEqual(
            line.vdi_line_risk_level,
            "critical",
        )

        self.assertFalse(
            line.vdi_data_issue,
        )

    def test_eta_extended_beyond_grace_is_at_risk(self):  # T12
            po = self._po(
                qty=100,
                days_ago=1,
            )
    
            line = po.order_line
    
            # Keep the original promise as baseline.
            original_promise = line.vdi_original_promise
    
            # Extend ETA beyond baseline + grace.
            line.date_planned = original_promise + timedelta(
                days=po.company_id.vdi_grace_days + 2,
            )
    
            # Leave the quantity completely open.
            line._vdi_refresh_metrics()
    
            print("T12 ORIGINAL PROMISE:", line.vdi_original_promise)
            print("T12 CURRENT ETA:", line.date_planned)
            print("T12 RISK:", line.vdi_line_risk_level)
    
            self.assertGreater(
                line.date_planned,
                original_promise + timedelta(
                    days=po.company_id.vdi_grace_days,
                ),
            )
    
            self.assertGreater(
                line.vdi_original_qty - line.vdi_net_received_qty,
                0,
            )
    
            self.assertEqual(
                line.vdi_line_risk_level,
                "at_risk",
            )

    def test_critical_supply_due_soon_is_at_risk(self):  # T13
        po = self._po(
            qty=100,
            days_ago=0,
        )

        line = po.order_line

        # Mark this line as a critical supply.
        line.vdi_is_critical_supply = True

        # Keep the full quantity open.
        line._vdi_refresh_metrics()

        print("T13 CRITICAL SUPPLY:", line.vdi_is_critical_supply)
        print("T13 RISK:", line.vdi_line_risk_level)

        self.assertTrue(
            line.vdi_is_critical_supply,
        )

        self.assertGreater(
            line.vdi_original_qty - line.vdi_net_received_qty,
            0,
        )

        self.assertEqual(
            line.vdi_line_risk_level,
            "at_risk",
        )

        self.assertNotEqual(
            line.vdi_line_risk_level,
            "due_soon",
        )

    def test_completed_po_retires_vdi_activity(self):  # T14
        po = self._po(qty=100, days_ago=10)

        # First partial receipt → PO remains at risk
        picking, backorder = self._receive_with_backorder(po, 60)
        self._set_done_date(picking, 12)
        print("T14 FIRST PICKING:", picking.id)
        for move in picking.move_ids:
            print(
                "T14 FIRST MOVE:",move.id,
                "STATE:", move.state,
                "QTY:", move.quantity,
                "PURCHASE LINE:", move.purchase_line_id.id,
                "PICKING TYPE:", move.picking_type_id.code,)

        po.action_vdi_refresh()

        activity = self.env["mail.activity"].search([
            ("res_model", "=", "purchase.order"),
            ("res_id", "=", po.id),
            ("vdi_generated", "=", True),
            ("active", "=", True),
        ], limit=1)

        self.assertTrue(activity)
        self.assertEqual(po.vdi_risk_level, "critical")

        # Complete the remaining quantity
        backorder.move_ids.quantity = 40
        backorder.with_context(skip_backorder=True).button_validate()
        print("T14 PO STATE:", po.state)
        print("T14 BACKORDER STATE:", backorder.state)
        print("T14 BACKORDER MOVES:", backorder.move_ids.mapped("state"))
        print(
            "T14 PURCHASE LINE IDS:",
            backorder.move_ids.mapped("purchase_line_id").ids,
        )
        print("T14 RECEIVED QTY:", po.order_line.vdi_net_received_qty)
        po.order_line._vdi_refresh_metrics()
        po.action_vdi_refresh()

        print("T14 RISK:", po.vdi_risk_level)
        print("T14 OPEN ACTIVITY:", activity.active)

        self.assertEqual(po.vdi_risk_level, "complete")
        self.assertFalse(activity.active)

    def test_cron_twice_creates_only_one_vdi_activity(self):  # T15
        po = self._po(qty=100, days_ago=10)

        picking, backorder = self._receive_with_backorder(po, 60)
        self._set_done_date(picking, 12)

        # First refresh
        self.env["purchase.order"]._cron_vdi_daily_refresh()

        activities_after_first = self.env["mail.activity"].search([
            ("res_model", "=", "purchase.order"),
            ("res_id", "=", po.id),
            ("vdi_generated", "=", True),
            ("active", "=", True),
        ])

        print(
            "T15 ACTIVITIES AFTER FIRST REFRESH:",
            activities_after_first.ids,
        )

        self.assertEqual(len(activities_after_first), 1)

        # Second refresh
        self.env["purchase.order"]._cron_vdi_daily_refresh()

        activities_after_second = self.env["mail.activity"].search([
            ("res_model", "=", "purchase.order"),
            ("res_id", "=", po.id),
            ("vdi_generated", "=", True),
            ("active", "=", True),
        ])

        print(
            "T15 ACTIVITIES AFTER SECOND REFRESH:",
            activities_after_second.ids,
        )

        self.assertEqual(len(activities_after_second), 1)
        self.assertEqual(
            activities_after_first.id,
            activities_after_second.id
        )

    def test_at_risk_to_critical_escalates_existing_activity(self):  # T16
        po = self._po(qty=100, days_ago=0)

        line = po.order_line

        # First state: At Risk
        line.vdi_is_critical_supply = True
        po.action_vdi_refresh()

        self.assertEqual(
            po.vdi_risk_level,
            "at_risk",
        )

        activity = self.env["mail.activity"].search([
            ("res_model", "=", "purchase.order"),
            ("res_id", "=", po.id),
            ("vdi_generated", "=", True),
            ("active", "=", True),
        ], limit=1)

        self.assertTrue(activity)

        activity_id = activity.id

        # Move the original promise into the past.
        old_promise = fields.Datetime.now() - timedelta(days=10)

        line.with_context(
            vdi_baseline_capture=True,
        ).write({
            "vdi_original_promise": old_promise,
        })

        line.date_planned = old_promise

        # Second state: Critical
        po.action_vdi_refresh()

        self.assertEqual(
            po.vdi_risk_level,
            "critical",
        )

        activities = self.env["mail.activity"].search([
            ("res_model", "=", "purchase.order"),
            ("res_id", "=", po.id),
            ("vdi_generated", "=", True),
            ("active", "=", True),
        ])

        # No duplicate activity.
        self.assertEqual(
            len(activities),
            1,
        )

        # Same activity must be escalated.
        self.assertEqual(
            activities.id,
            activity_id,
        )

        self.assertEqual(
            activities.summary,
            "VDI Delivery Risk Escalated",
        )

    def test_cancelled_po_has_no_open_risk(self):
        # T18: Cancelled PO must not show an open delivery-risk warning.
        order = self.env["purchase.order"].create({
            "partner_id": self.vendor.id,
            "order_line": [
                Command.create({
                    "product_id": self.product.id,
                    "product_qty": 100,
                    "price_unit": 10,
                    "date_planned": fields.Datetime.now() - timedelta(days=3),
                }),
            ],
        })

        order.button_confirm()
        order.button_cancel()
        order.action_vdi_refresh()

        self.assertEqual(order.vdi_risk_level, "not_applicable")
        self.assertEqual(order.vdi_open_line_count, 0)
        self.assertEqual(order.vdi_critical_line_count, 0)