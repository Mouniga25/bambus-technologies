from odoo import api, fields, models, _, Command


class DepartmentInfo(models.Model):
    _name = 'department.info'
    _description = "department Info"
    
    name = fields.Char(string="Staff Name")
    department_id= fields.Integer(string="staff department")

   
                          