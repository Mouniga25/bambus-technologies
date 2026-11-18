from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class DepartmentInformation(models.Model):
    _name = 'department.information'
    _description = "department Information"
    _rec_name ="name"


    name = fields.Char(string="Department Name")
    department_code= fields.Char(string="Department Code")
    department_date = fields.Date(string=" Department Date")
    display_name = fields.Char(compute="_compute_display_name")


    student_count = fields.Integer(
        string="Students",
        compute="_compute_counts"
    )
    
    faculty_count = fields.Integer(
        string="Faculty count",
        compute="_compute_counts"
    )

    student_ids = fields.One2many('student.information', 'department_id')
    faculty_ids = fields.One2many('faculty.information', 'department_id')


# Onchange
    @api.onchange("name")
    def onchange_name(self):
        print(self,"------------")
        if self.name == "test":
            raise ValidationError("You can't give name as 'test'")

# display name
    """display_name is  display two field top right side of the form view"""
    @api.depends('name','department_code')
    def _compute_display_name(self):
        for record in self:
            if record.name and record.department_code:
                record.display_name = f"[{record.department_code}] - {record.name}"
            else:
                record.display_name = record.name
    
    """serach"""
    @api.model
    def name_search(self, name='',args=None, operator='ilike',limit=100):
        args = args or []
        domain = []
        if name:
            domain = [
                '|','|',
                ('department_code',operator,name),
                ('name',operator,name),
                ('department_date',operator,name),
            ]
        final_domain = args + domain
        partners = self.search(final_domain, limit=limit)
        return[(partner.id, partner.display_name) for partner in partners]

#compute field
    @api.depends('student_ids', 'faculty_ids') 
    def _compute_counts(self):
        for rec in self:
            rec.student_count = self.env['student.information'].search_count([('department_id', '=', rec.id)])
            rec.faculty_count = self.env['faculty.information'].search_count([('department_id', '=', rec.id)])
    

# smart button
    def action_view_faculty(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Faculty',
            'res_model': 'faculty.information',
            'view_mode': 'list,form',
            'domain': [('department_id', '=', self.id)],
            'context': {'default_department_id': self.id}
            }
  

    def action_view_students(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students',
            'res_model': 'student.information',
            'view_mode': 'list,form',
            'domain': [('department_id', '=', self.id)],
            'context': {'default_department_id': self.id}
            }
    

