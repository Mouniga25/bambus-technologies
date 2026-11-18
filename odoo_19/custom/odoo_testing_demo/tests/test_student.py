from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, AccessError


class TestStudent(TransactionCase):
    def setUp(self):
        super().setUp()

        # Common student record
        self.student = self.env['test.student'].create({
            'name': 'Mouniga',
            'age': 22,
            'email': 'mouniga@example.com',
        })

        self.assertTrue(self.student)

        # Test user for security testing
        self.test_user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_user_security',
        })

    # -------------------------
    # CREATE / READ
    # -------------------------

    def test_student_age(self):
        self.assertEqual(self.student.age, 22)
    def test_create_and_read_student(self):
        self.assertTrue(self.student)
        self.assertEqual(self.student.name, 'Mouniga')
        self.assertEqual(self.student.age, 22)
        self.assertEqual(self.student.email,'mouniga@example.com')
    # -------------------------
    # UPDATE
    # -------------------------
    def test_update_student(self):
        self.student.write({
            'age': 23,
        })

        self.assertEqual(self.student.age, 23)

    # -------------------------
    # DELETE
    # -------------------------

    def test_delete_student(self):
        student = self.env['test.student'].create({
            'name': 'Mouniga',
            'age': 22,
            'email': 'mouniga@example.com',
        })

        student.unlink()

        self.assertFalse(student.exists())

    # -------------------------
    # CONSTRAINT
    # -------------------------

    def test_update_negative_age(self):
        with self.assertRaises(ValidationError):
            self.student.write({
                'age': -5,
            })

    # -------------------------
    # COMPUTE
    # -------------------------

    def test_compute_double_age(self):
        self.assertEqual(
            self.student.double_age,
            44
        )

    # -------------------------
    # ONCHANGE
    # -------------------------

    def test_onchange_age(self):
        student = self.env['test.student'].new({
            'name': 'Mouniga',
            'age': 22,
        })

        student._onchange_age()

        self.assertEqual(
            student.email,
            'adult@example.com'
        )

    # -------------------------
    # BUSINESS LOGIC
    # -------------------------

    def test_action_pass(self):
        self.student.action_pass()

        self.assertEqual(
            self.student.email,
            'passed@example.com'
        )

    # -------------------------
    # SECURITY
    # -------------------------

    def test_user_cannot_create_student(self):
        with self.assertRaises(AccessError):
            self.env['test.student'].with_user(
                self.test_user
            ).create({
                'name': 'Test Student',
                'age': 22,
            })
    def test_user_cannot_delete_student(self):
        with self.assertRaises(AccessError):
            self.env['test.student'].with_user(
                self.test_user
            ).browse(self.student.id).unlink()