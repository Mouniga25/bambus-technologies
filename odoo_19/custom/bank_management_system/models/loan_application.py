from odoo import api, fields, models


class LoanApplication(models.Model):
    _name = 'loan.application'
    _description = 'Loan Application'
    _rec_name = 'loan_sequence'

    loan_sequence = fields.Char(string="Loan Sequence",required=True,copy=False,readonly=True,default="New")
    customer_id = fields.Many2one('customer.information',string="Customer Name",required=True)
    assigned_officer_id = fields.Many2one('employee.information',string="Assigned Officer",required=True)
    branch_id = fields.Many2one('branch.information',string="Branch",related='assigned_officer_id.branch_id',store=True,readonly=True)
    date_of_application = fields.Date(string="Date of Application",default=fields.Date.today)
    principal_amount = fields.Float(string="Principal Amount" )
    interest_rate = fields.Float(string="Interest Rate")
    processing_fee = fields.Float(string="Processing Fee")
    total_loan_cost = fields.Float(string="Total Loan Cost",compute="_compute_total_loan_cost",store=True)
    submitted_document_ids = fields.One2many('loan.document.line','loan_id',string="Submitted Documents")



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('loan_sequence', 'New') == 'New':
                vals['loan_sequence'] = (
                    self.env['ir.sequence'].next_by_code('loan.application')
                    or 'New'
                )

        return super().create(vals_list)

    @api.depends('principal_amount', 'processing_fee')
    def _compute_total_loan_cost(self):
        for record in self:
            record.total_loan_cost = (
                record.principal_amount + record.processing_fee
            )
class LoanDocumentLine(models.Model):
    _name = 'loan.document.line'
    _description = 'Loan Document'

    loan_id = fields.Many2one('loan.application',string="Loan Application",required=True,ondelete='cascade')
    document_name = fields.Char(string="Document Name",required=True)
    document_type = fields.Selection([
        ('id_proof', 'ID Proof'),
        ('address_proof', 'Address Proof'),
        ('income_proof', 'Income Proof'),
    ], string="Document Type")
    attachment = fields.Binary(string="Attachment")
    verified = fields.Boolean(string="Verified",default=False)