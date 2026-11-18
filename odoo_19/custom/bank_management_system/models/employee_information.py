from odoo import api, fields, models
from datetime import date


class EmployeeInformation(models.Model):
    _name = 'employee.information'
    _description = "Employee Information"



    name = fields.Char(string="Name")
    last_name=fields.Char(string="Last Name")
    photo = fields.Binary(string ="Image")
    job_position = fields.Selection([('branch_manager','Branch Manager'),
                                    ('teller','Teller'),
                                ('loan_officer','Loan Officer'),
                                ('clerk','Clerk')])
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(string="Age")
    gender = fields.Selection([('female','Female'),
                                ('male','Male'),
                                ('other','Other')
                                ])
    branch_id = fields.Many2one(
        'branch.information',
        string="Branch"
    )
    qualifications_ids = fields.Many2many(
        'qualifications.information',
        string="Qualifications"
    )

    total_accounts_handled = fields.Integer(string="Total Accounts Handled",
                         compute = "_compute_total_accounts_handled",
                          store=True)
    dependent_ids = fields.One2many('employee.dependent.line','employee_id', string="Dependent Details")
    account_lines = fields.One2many(
    'bank.accounts',
    'employee_id',
    string="Accounts Handled")
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        readonly=True
    )
    address = fields.Char(string="Address")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")

    # Professional Information
    hire_date = fields.Date(string="Hire Date")
    salary = fields.Float(string="Salary")

    access_level = fields.Selection([
        ('level_1', 'Level 1'),
        ('level_2', 'Level 2'),
        ('level_3', 'Level 3'),
    ], string="Access Level")

    
    """Calculate the total account handled"""
    def _compute_total_accounts_handled(self):
        for record in self:
            record.total_accounts_handled = self.env['bank.accounts'].search_count([
                ('employee_id', '=', record.id)
            ])

    """Onchange using age calculation"""
    @api.onchange('date_of_birth')
    def _onchange_age(self):
        for record in self:
            if record.date_of_birth:
                today = date.today()
                record.age = today.year - record.date_of_birth.year
            else:
                record.age = 0


class EmployeeDependentLine(models.Model):
    _name = 'employee.dependent.line'
    _description = 'Employee Dependent Details'

    employee_id = fields.Many2one(comodel_name='employee.information')

    
    dependent_name = fields.Char(string="Dependent Name")
    relationship = fields.Selection([('mother','Mother'),
                                    ('father','Father'),
                                ('brother','Brother'),
                                ('sister','Sister'),
                                ('husband','Husband'),
                                ('wife','Wife')])
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(string="Age")
    

  
    """Onchange using age calculation"""
    @api.onchange('date_of_birth')
    def _onchange_age(self):
        for record in self:
            if record.date_of_birth:
                today = date.today()
                record.age = today.year - record.date_of_birth.year
            else:
                record.age = 0
    

    
