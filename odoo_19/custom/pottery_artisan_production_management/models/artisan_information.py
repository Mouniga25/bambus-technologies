from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Artisan(models.Model):
    _name = 'village.artisan'
    _description = 'Artisan Information'
    _order = 'partner_id'
    _rec_name = 'partner_id'

    #sequence
    artisan_code = fields.Char(string="Artisan Code",required=True,copy=False,readonly=True,default='New')

    #artisan details
    partner_id = fields.Many2one('res.partner',string='Artisan Name',required=True,domain=[('is_artisan', '=', True)])
    phone = fields.Char(related='partner_id.phone',string='Phone',readonly=True)
    email = fields.Char(related='partner_id.email',string='Email',readonly=True)
    address = fields.Char(related='partner_id.contact_address',string='Address',readonly=True)
    skill = fields.Char(related='partner_id.artisan_skill',string='Skill',store=True,readonly=True)
    experience = fields.Integer(related='partner_id.artisan_experience',string='Experience (Years)',store=True,readonly=True)
    artisan_type = fields.Selection([('full_time', 'Full Time'),('part_time', 'Part Time'),('contract', 'Contract'),],string='Artisan Type',default='full_time')
    active = fields.Boolean(string='Active',default=True)
    production_count = fields.Integer(string='Productions',compute='_compute_production_count')
    settlement_count = fields.Integer(string='Settlements',compute='_compute_settlement_count')
    labour_rate = fields.Float(string='Labour Rate', default=0.0)
    
    #sequence creation
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('artisan_code', 'New') == 'New':
                vals['artisan_code'] = self.env[
                    'ir.sequence'
                ].next_by_code('village.artisan') or 'New'
        return super().create(vals_list)

#########
# compute fields
#########
    @api.depends('artisan_code', 'partner_id.name')
    def _compute_display_name(self):
        for record in self:
            if record.artisan_code and record.partner_id:
                record.display_name = (f"{record.artisan_code} - {record.partner_id.name}")
            else:
                record.display_name = record.partner_id.name or 'New'

#########
# constrains
#########
    #---------Experience cannot be negative--------
    @api.constrains('experience')
    def _check_experience(self):
        for record in self:
            if record.experience < 0:
                raise ValidationError('Experience cannot be negative.')

#########
# button
#########
    def _compute_production_count(self):
        for record in self:
            record.production_count = self.env['production.information'].search_count([('artisan_id', '=', record.id)])
    def action_view_productions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Productions',
            'res_model': 'production.information',
            'view_mode': 'list,form',
            'domain': [
                ('artisan_id', '=', self.id)
            ],
            'context': {
                'default_artisan_id': self.id
            },
        }
    def _compute_settlement_count(self):
        for record in self:
            record.settlement_count = self.env['settlement.information'].search_count([('artisan_id', '=', record.id)])

    def action_view_settlements(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Settlements',
            'res_model': 'settlement.information',
            'view_mode': 'list,form',
            'domain': [('artisan_id', '=', self.id)],
            'context': {'default_artisan_id': self.id},
        }

    
# -----------delete---------------
    def unlink(self):
        for record in self:
            production_count = self.env['production.information'].search_count([('artisan_id', '=', record.id)])
            if production_count:
                raise ValidationError('Artisan cannot be deleted because production records exist.')
        return super().unlink()        