from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBaseline(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Vendor A"})
        cls.product = cls.env["product.product"].create(
            {"name": "Widget", "is_storable": True},
        )

    def _make_po(self, qty=10, days=5):
        return self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    (0, 0, {
                        "product_id": self.product.id,
                        "product_qty": qty,
                        "price_unit": 1.0,
                        "date_planned": fields.Datetime.now() + timedelta(days=days),
                    }),
                ],
            },
        )

    def test_draft_has_no_baseline(self):  # T01
        po = self._make_po()
        self.assertFalse(po.order_line.vdi_original_promise)

    def test_confirm_captures_baseline(self):
        po = self._make_po()
        planned = po.order_line.date_planned
        po.button_confirm()
        self.assertEqual(po.order_line.vdi_original_promise, planned)
        self.assertEqual(po.order_line.vdi_original_qty, 10)

    def test_eta_edit_keeps_baseline(self):  # T02
        po = self._make_po()
        po.button_confirm()
        original = po.order_line.vdi_original_promise
        po.order_line.date_planned += timedelta(days=8)
        self.assertEqual(po.order_line.vdi_original_promise, original)
        self.assertEqual(po.order_line.vdi_eta_shift_days, 8)

    def test_frozen_fields_protected(self):
        po = self._make_po()
        po.button_confirm()
        with self.assertRaises(UserError):
            po.order_line.vdi_original_qty = 99

    def test_duplicate_has_no_snapshot(self):  # T19
        po = self._make_po()
        po.button_confirm()
        new_po = po.copy()
        self.assertFalse(new_po.order_line.vdi_original_promise)
        new_po.button_confirm()
        self.assertTrue(new_po.order_line.vdi_original_promise)
