from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class KilnInformation(models.Model):
    _name = 'kiln.information'
    _description = 'Kiln Information'
    _order = 'name'

    kiln_code = fields.Char(string='Kiln Code',copy=False,readonly=True)
    name = fields.Char(string='Kiln Name',required=True)
    capacity = fields.Float(string='Capacity',required=True)
    kiln_type = fields.Selection([('wood', 'Wood Fired'),('gas', 'Gas Fired'),('electric', 'Electric'),('traditional', 'Traditional'),],string='Kiln Type',required=True )
    status = fields.Selection([('available', 'Available'),('in_use', 'In Use'),('maintenance', 'Maintenance'),('inactive', 'Inactive'),],string='Status',default='available',required=True)
    last_maintenance = fields.Date(string='Last Maintenance')
    maintenance_interval = fields.Integer(string='Maintenance Interval (Days)',default=30,required=True)
    maintenance_due = fields.Boolean(string='Maintenance Due',compute='_compute_maintenance_due',store=True)
    maintenance_mail_sent = fields.Boolean(string='Maintenance Mail Sent',default=False)
    production_ids = fields.One2many('production.information','kiln_id',string='Productions')


    @api.depends('production_ids')
    def _compute_production_count(self):
        for record in self:
            record.production_count = len(record.production_ids)
    production_count = fields.Integer(string='Productions Processed',compute='_compute_production_count')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('kiln_code'):
                vals['kiln_code'] = self.env['ir.sequence'].next_by_code('kiln.information') or 'New'

        return super().create(vals_list)
    
    @api.constrains('capacity')
    def _check_capacity(self):
        for record in self:
            if record.capacity <= 0:
                raise ValidationError('Kiln Capacity must be greater than zero.')
    @api.constrains('maintenance_interval')
    @api.constrains('maintenance_interval')
    def _check_maintenance_interval(self):
        for record in self:
            if record.maintenance_interval <= 0:
                raise ValidationError('Maintenance Interval must be greater than zero.')

    @api.depends('last_maintenance', 'maintenance_interval')
    def _compute_maintenance_due(self):
        today = fields.Date.today()

        for record in self:
            if not record.last_maintenance:
                record.maintenance_due = False
                continue    
            due_date = record.last_maintenance + timedelta(days=record.maintenance_interval)

            record.maintenance_due = today >= due_date  

    def _check_maintenance_interval(self):
        for record in self:
            if record.maintenance_interval <= 0:
                raise ValidationError('Maintenance Interval must be greater than zero.')

    def action_set_available(self):
        for record in self:
            record.status = 'available'

    def action_set_in_use(self):
        for record in self:
            if record.status == 'maintenance':
                raise ValidationError('Kiln under maintenance cannot be marked as In Use.')

            record.status = 'in_use'

    def action_set_maintenance(self):
        for record in self:
            record.status = 'maintenance'

    #######
    #Cron
    #######
    @api.model
    def _cron_check_maintenance_due(self):

        maintenance_due_kilns = self.search([('maintenance_due', '=', True),('status', '!=', 'maintenance'),('status', '!=', 'inactive'),('maintenance_mail_sent', '=', False),])
        template = self.env.ref('pottery_artisan_production_management.mail_template_kiln_maintenance_due')

        for kiln in maintenance_due_kilns:
            template.send_mail(kiln.id,force_send=True)
            kiln.maintenance_mail_sent = True

        return maintenance_due_kilns

    def unlink(self):
        for record in self:
            if record.production_ids:
                raise ValidationError('This kiln cannot be deleted because it has already been used for production.')
        return super().unlink()