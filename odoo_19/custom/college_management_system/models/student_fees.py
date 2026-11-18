from odoo import api, fields, models


class StudentFees(models.Model):
    _name = 'student.fees'
    _description = 'Student Fees'
    _rec_name = 'fees_sequence'

    fees_sequence = fields.Char(
        string="Fees Sequence",
        default="New",
        readonly=True,
        copy=False
    )

    student_id = fields.Many2one(
        'student.information',
        string="Student Name",
        required=True
    )

    semester = fields.Selection(
        related='student_id.semester',
        string="Semester",
        store=True,
        readonly=True
    )

    department_id = fields.Many2one(
        related='student_id.department_id',
        string="Department",
        store=True,
        readonly=True
    )

    date_of_payment = fields.Date(
        string="Date of Payment",
        default=fields.Date.today
    )
    fees_sequence = fields.Char(
    string="Fees Sequence",
    default="New",
    readonly=True,
    copy=False)

    tuition_fee = fields.Float(string="Tuition Fee")
    examination_fee = fields.Float(string="Examination Fee")
    bus_fee = fields.Float(string="Bus Fee")
    hostel_fee = fields.Float(string="Hostel Fee")
    mess_fee = fields.Float(string="Mess Fee")

    total_fee = fields.Float(
        string="Total Fee",
        compute="_compute_total_fee",
        store=True
    )

    @api.depends(
        'tuition_fee',
        'examination_fee',
        'bus_fee',
        'hostel_fee',
        'mess_fee'
    )
    def _compute_total_fee(self):
        for record in self:
            record.total_fee = (
                record.tuition_fee
                + record.examination_fee
                + record.bus_fee
                + record.hostel_fee
                + record.mess_fee
            )