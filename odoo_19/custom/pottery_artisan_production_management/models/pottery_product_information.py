from odoo import models, fields,api
from odoo.exceptions import ValidationError


class PotteryProductInformation(models.Model):
    _name = 'pottery.product.information'
    _description = 'Pottery Product Information'
    _order = 'name'


    #Sequence
    product_code = fields.Char(string='Product Code',required=True,copy=False,readonly=True,default='New')

    name = fields.Char(string='Product Name',required=True)
    product_type = fields.Selection([('water_pot', 'Water Pot'),('cooking_pot', 'Cooking Pot'),('flower_vase', 'Flower Vase'),('diya', 'Diya'),('decorative', 'Decorative'),('other', 'Other'),],string='Product Type',required=True)
    description = fields.Html(string='Description')
    selling_price = fields.Float(string='Selling Price',required=True)
    cost_price = fields.Float(string='Cost Price',required=True)
    active = fields.Boolean(string='Active',default=True)
    production_lines = fields.One2many('production.information','product_id',string='Productions')
    raw_material_ids = fields.Many2many('raw.material.information',string='Raw Materials')
    production_count = fields.Integer(string='Production Orders',compute='_compute_production_count')
    profit_amount = fields.Float(string='Profit Amount',compute='_compute_profit_amount',store=True)
    product_count = fields.Integer(string='Products',compute='_compute_product_count')
    clay_required_per_unit = fields.Float(string='Clay Required Per Unit (KG)')
    raw_material_lines = fields.One2many('product.raw.material.line','product_id',string='Raw Material')
    image = fields.Binary(string='Product Image',attachment=True)
    
    """Selling Price Validation"""
    @api.constrains('selling_price', 'cost_price')
    def _check_selling_price(self):
        for record in self:
            if record.selling_price <= record.cost_price:
                raise ValidationError('Selling Price must be greater than Cost Price.')

    # Sequence
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('product_code', 'New') == 'New':
                vals['product_code'] = self.env['ir.sequence'].next_by_code('pottery.product') or 'New'
        return super().create(vals_list)


#######
#Smart button 
#######
    @api.depends('production_lines')
    def _compute_production_count(self):
        for record in self:
            record.production_count = len(record.production_lines)

    def action_view_productions(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Production Orders',
            'res_model': 'production.information',
            'view_mode': 'list,form',
            'domain': [('product_id', '=', self.id)],
            'context': {
                'default_product_id': self.id,
            },
        }

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
        }


    @api.depends('selling_price', 'cost_price')
    def _compute_profit_amount(self):
        for record in self:
            record.profit_amount = (record.selling_price - record.cost_price)


    @api.depends('name', 'product_code')
    def _compute_display_name(self):
        for record in self:
            if record.product_code and record.name:
                record.display_name = (f'{record.product_code} - {record.name}')
            elif record.name:
                record.display_name = record.name
            else:
                record.display_name = record.product_code or ''


    def action_get_raw_material_names(self):
        products = self
        material_names = products.mapped('raw_material_ids.name')

        return material_names


    def unlink(self):
        for record in self:
            production_exists = self.env['production.information'].search_count([('product_id', '=', record.id)])
            order_exists = self.env['customer.order.line'].search_count([('product_id', '=', record.id)])
            if production_exists or order_exists:
                raise ValidationError('Product cannot be deleted because it is used in ''Production or Customer Orders.')
        return super().unlink()


