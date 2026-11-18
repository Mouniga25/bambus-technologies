from odoo import api, fields, models

class QualificationsInformation(models.Model):
    _name = 'qualifications.information'
    _description = "Qualifications Information"
    _rec_name ="qualifications_name"



    qualifications_code = fields.Char(string="Qualifications Code", required =True, copy = False, readonly = True, default = 'New')
    qualifications_name = fields.Char(string="Qualifications Name")

    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            if vals.get('qualifications_code','New')=='New':
                vals['qualifications_code'] = self.env['ir.sequence'].next_by_code('qualifications.code') or 'New'
        return super().create(vals_list)







