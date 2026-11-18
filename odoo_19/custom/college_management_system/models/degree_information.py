from odoo import api, fields, models, _, Command


class DegreeInformation(models.Model):
    _name = 'degree.information'
    _description = "Degree Information"
    
    name = fields.Char(string="Degree Name")
    degree_code = fields.Integer(string="Degree Code")

    degree_lines = fields.One2many(comodel_name="degree.information.line", 
                                   inverse_name = 'degree_id')
    
#    ###########
#     action
#     ############
    def action_click(self):
        action_ref = self.env.ref('college_management_system.action_popup_information').read()[0]
        return action_ref


class DegreeInformationLine(models.Model):
    _name = 'degree.information.line'
    _description = 'Degree Information Line'


    degree_id = fields.Many2one(comodel_name='degree.information')
   

    degree_name = fields.Char(string="Name")
    code = fields.Integer(string="Code")
    phone = fields.Char(string='Phone')
   

    ############
    # action
    #############
    def action_click(self):
        action_ref = self.env.ref('college_management_system.action_popup_information').read()[0]
        return action_ref
    


    # @api.model
    # def default_get(self,fields_list):
    #     res = {}
    #     degree = self.env.ref['degree.information.line'].browse(self.env.context.get())
    #     res.update({'name' :degree.degree_name,
    #                 'code' :degree.code,
    #                 'phone' :degree. phone })
    #     return res
    

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        degree_id = self.env.context.get('active_id')

        if degree_id:
            degree = self.env['degree.information.line'].browse(degree_id)

            res.update({
                'degree_name': degree.degree_name,
                'code': degree.code,
                'phone': degree.phone,
         })
        return res

    





  




