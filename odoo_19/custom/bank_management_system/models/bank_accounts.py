from odoo import api, fields, models
from datetime import date

class BankAccount(models.Model):
    _name = 'bank.accounts'
    _description = "Bank Account"
    # _inherit = 'customer.information'



    account_number = fields.Char(string="reference", required = True, copy=False, readonly = True, default = "New")
    customer_id = fields.Many2one('customer.information',string="Customer Name")
    employee_id = fields.Many2one('employee.information',string="Handled By")
    account_type_id = fields.Many2one('account.type',string="Account Type")
    home_branch_id = fields.Many2one('branch.information',string="Home Branch",related='customer_id.home_branch_id',store=True,readonly=True)
    opening_date = fields.Date(string="Opening Date")
    account_status = fields.Selection([('active',' Active'),
                                    ('dormant','Dormant'),
                                ('closed','Closed')])
    transaction_line = fields.One2many('bank.transaction.line','account_id',string="Transaction Lines")
    # Current Balance
    current_balance = fields.Float(string="Current Balance",compute="_compute_current_balance",store=True)
    
    # Sequence
    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            if vals.get('account_number','New')=='New':
                vals['account_number'] = self.env['ir.sequence'].next_by_code('account.number') or 'New'
        return super().create(vals_list)

    # Compute Current Balance
    @api.depends(
        'transaction_line.amount',
        'transaction_line.transaction_type'
    )
    def _compute_current_balance(self):
        for record in self:
            balance = 0.0

            for transaction in record.transaction_line:
                if transaction.transaction_type == 'deposit':
                    balance += transaction.amount
                elif transaction.transaction_type == 'withdrawal':
                    balance -= transaction.amount

            record.current_balance = balance



class BankTransactionLine(models.Model):
    _name = 'bank.transaction.line'
    _description = 'Bank Transaction Line'

    account_id = fields.Many2one(
        'bank.accounts',
        string="Account"
    )

    transaction_date = fields.Date(
        string="Transaction Date"
    )

    transaction_type = fields.Selection([
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ], string="Transaction Type")

    reference = fields.Text(
        string="Reference / Narration"
    )

    amount = fields.Float(
        string="Amount"
    )   
    employee_id = fields.Many2one(
    'employee.information',
    string="Handled By") 
    
    





    
