from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RawMaterialInformation(models.Model):
    _name = 'raw.material.information'
    _description = 'Raw Material Information'
    _order = 'name'

    #Sequence
    material_code = fields.Char(string='Material Code',required=True,copy=False,readonly=True,default='New')
    product_ids = fields.Many2many('pottery.product.information',string='Pottery Products')
    name = fields.Char(string='Material Name',required=True)
    
    unit = fields.Selection([('kg', 'Kg'),('gram', 'Gram'),('litre', 'Litre'),('piece', 'Piece'),],string='Unit',required=True)
    available_quantity = fields.Float(string='Available Quantity',default=0.0)
    minimum_quantity = fields.Float(string='Minimum Quantity',default=0.0)
    unit_cost = fields.Float(string='Unit Cost',required=True)
    active = fields.Boolean(string='Active',default=True)
    stock_status = fields.Selection([('available', 'Available'),('low', 'Low Stock'),],string='Stock Status',compute='_compute_stock_status',store=True)
    product_count = fields.Integer(string='Products',compute='_compute_product_count')


    # Sequence
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('material_code', 'New') == 'New':
                vals['material_code'] = self.env[
                    'ir.sequence'
                ].next_by_code(
                    'raw.material'
                ) or 'New'

        return super().create(vals_list)

     # Default values
    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)

        vals['active'] = True
        vals['unit'] = 'kg'

        return vals
    
    @api.depends('available_quantity', 'minimum_quantity')
    def _compute_stock_status(self):
        for record in self:
            if record.available_quantity <= record.minimum_quantity:
                record.stock_status = 'low'
            else:
                record.stock_status = 'available'

    @api.constrains(
        'available_quantity',
        'minimum_quantity',
        'unit_cost',
        'material_code'
    )
    def _check_values(self):
        for record in self:

            if record.available_quantity < 0:
                raise ValidationError(
                    'Available Quantity cannot be negative.'
                )

            if record.minimum_quantity < 0:
                raise ValidationError(
                    'Minimum Quantity cannot be negative.'
                )

            if record.unit_cost < 0:
                raise ValidationError(
                    'Unit Cost cannot be negative.'
                )

            # Duplicate Material Code
            duplicate = self.search([
                ('material_code', '=', record.material_code),
                ('id', '!=', record.id)
            ], limit=1)

            if duplicate:
                raise ValidationError(
                    'Material Code must be unique.'
                )
    def action_open_stock_wizard(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock Adjustment',
            'res_model': 'raw.material.stock.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_raw_material_id': self.id,
                'default_current_quantity': self.available_quantity,
            },
        }
######3
#Smart button
#######
    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['pottery.product.information'].search_count([('raw_material_ids', 'in', record.id)])

    def action_view_products(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Pottery Products',
            'res_model': 'pottery.product.information',
            'view_mode': 'list,form',
            'domain': [('raw_material_ids', 'in', self.id)],
            'context': {'default_raw_material_ids': [self.id]
            },
        }

    def unlink(self):
        for record in self:
            product_exists = self.env['pottery.product.information'].search_count([('raw_material_ids', 'in', record.id)])
            if product_exists:
                raise ValidationError(
                    'Raw Material cannot be deleted because it is used '
                    'in a Product.'
                )

        return super().unlink()