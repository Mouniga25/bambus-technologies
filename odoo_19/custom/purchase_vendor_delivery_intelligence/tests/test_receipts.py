from datetime import timedelta

from odoo import fields
from odoo.tests import Form
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReceiptEvidence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.vendor = cls.env["res.partner"].create(
            {"name": "Vendor R"},
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Widget R",
                "is_storable": True,
            },
        )

    def _po(self, qty=100):
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": qty,
                            "price_unit": 1.0,
                            "date_planned": (
                                fields.Datetime.now()
                                + timedelta(days=5)
                            ),
                        },
                    ),
                ],
            },
        )
        po.button_confirm()
        return po

    def _receive(self, po, qty):
        picking = po.picking_ids.filtered(
            lambda p: p.state != "done",
        )[:1]

        picking.move_ids.quantity = qty
        picking.with_context(
            skip_backorder=True,
        ).button_validate()

        return picking

    def test_partial_receipt_evidence(self):  # T03 base
        po = self._po(100)

        self._receive(po, 60)

        line = po.order_line
        ev = line._vdi_receipt_evidence()[line.id]

        self.assertEqual(
            len(ev["tranches"]),
            1,
        )
        self.assertEqual(
            ev["tranches"][0]["net"],
            60,
        )
        self.assertFalse(
            ev["issues"],
        )

    def test_no_receipt_no_tranche(self):
        po = self._po(10)

        line = po.order_line
        ev = line._vdi_receipt_evidence()[line.id]

        self.assertEqual(
            ev["tranches"],
            [],
        )

    def test_return_reduces_correct_accepted_tranche(self):  # T05
        po = self._po(100)

        # Receive 60 units.
        receipt = self._receive(po, 60)

        # Create return from the same receipt.
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=receipt.ids,
                active_id=receipt.id,
                active_model="stock.picking",
            ),
        )

        stock_return_picking = stock_return_picking_form.save()

        stock_return_picking.product_return_moves.quantity = 20.0

        return_action = (
            stock_return_picking.action_create_returns()
        )

        return_picking = self.env["stock.picking"].browse(
            return_action["res_id"],
        )

        # Validate the return.
        return_picking.move_ids[0].move_line_ids[0].quantity = 20.0
        return_picking.move_ids[0].picked = True
        return_picking._action_done()

        # Refresh VDI metrics.
        line = po.order_line
        line._vdi_refresh_metrics()

        # 60 received - 20 returned = 40 accepted.
        ev = line._vdi_receipt_evidence()[line.id]

        self.assertEqual(
            len(ev["tranches"]),
            1,
        )
        self.assertAlmostEqual(
            ev["tranches"][0]["received"],
            60.0,
        )
        self.assertAlmostEqual(
            ev["tranches"][0]["returned"],
            20.0,
        )
        self.assertAlmostEqual(
            ev["tranches"][0]["net"],
            40.0,
        )

    def test_unlinked_return_excluded_with_data_gap(self):  # T06
        po = self._po(100)
        line = po.order_line

        # Create a completed return move that is intentionally
        # not linked to any receipt or purchase return chain.
        StockMove = self.env["stock.move"]

        unlinked_return = StockMove.create(
            {
                "product_id": self.product.id,
                "product_uom_qty": 20.0,
                "product_uom": self.product.uom_id.id,
                "location_id": self.env.ref(
                    "stock.stock_location_stock",
                ).id,
                "location_dest_id": self.env.ref(
                    "stock.stock_location_suppliers",
                ).id,
                "purchase_line_id": line.id,
                "origin_returned_move_id": False,
            },
        )

        unlinked_return.quantity = 20.0
        unlinked_return.picked = True
        unlinked_return._action_done()

        ev = line._vdi_receipt_evidence()[line.id]

        # The unlinked return must not create a receipt tranche.
        self.assertEqual(
            ev["tranches"],
            [],
        )

        # It must be reported as a data issue.
        self.assertTrue(
            ev["issues"],
        )
        self.assertTrue(
            any(
                "is not linked to a receipt" in issue
                for issue in ev["issues"]
            ),
        )

        # Refresh VDI metrics and verify Data Gap.
        line._vdi_refresh_metrics()

        self.assertEqual(
            line.vdi_line_risk_level,
            "data_gap",
        )
    def test_different_uom_receipt_conversion(self):  # T07
        kg_uom = self.env.ref("uom.product_uom_kgm")
        gram_uom = self.env.ref("uom.product_uom_gram")

        po = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": 1.0,
                            "product_uom_id": kg_uom.id,
                            "price_unit": 1.0,
                            "date_planned": (
                                fields.Datetime.now()
                                + timedelta(days=5)
                            ),
                        },
                    ),
                ],
            },
        )
        po.button_confirm()

        line = po.order_line

        picking = po.picking_ids.filtered(
            lambda p: p.state != "done",
        )[:1]

        move = picking.move_ids.filtered(
            lambda m: m.purchase_line_id == line,
        )

        # Receipt is in grams while purchase commitment is in kg.
        move.product_uom = gram_uom
        move.product_uom_qty = 1000.0
        move.quantity = 1000.0

        picking.with_context(
            skip_backorder=True,
        ).button_validate()

        line._vdi_refresh_metrics()

        ev = line._vdi_receipt_evidence()[line.id]

        self.assertEqual(
            len(ev["tranches"]),
            1,
        )

        # 1000 grams = 1 kilogram.
        self.assertAlmostEqual(
            ev["tranches"][0]["received"],
            1.0,
            places=4,
        )

        self.assertAlmostEqual(
            ev["tranches"][0]["net"],
            1.0,
            places=4,
        )

    def test_zero_original_qty_excluded_with_explanation(self):  # T08
        po = self._po(1)
        line = po.order_line

        # Force the frozen baseline quantity to zero.
        line.with_context(
            vdi_baseline_capture=True,
        ).write(
            {
                "vdi_original_qty": 0.0,
            },
        )

        # Refresh must not crash.
        line._vdi_refresh_metrics()

        # Zero baseline quantity must not be scored.
        self.assertFalse(line.vdi_sample_eligible)

        # Risk must explain the data problem.
        self.assertIn(
            "quantity",
            (line.vdi_data_issue or "").lower(),
        )