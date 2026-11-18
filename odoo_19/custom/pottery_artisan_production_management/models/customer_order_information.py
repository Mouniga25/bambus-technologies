from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CustomerOrderInformation(models.Model):
    _name = 'customer.order.information'
    _description = 'Customer Order Information'
    _order = 'order_date desc'

    customer_id = fields.Many2one('res.partner',string='Customer',required=True,domain=[('is_artisan', '=', False)])
    name = fields.Char(string='Order Reference',required=True,copy=False,default='New' )
    
    order_date = fields.Date(string='Order Date',required=True,default=fields.Date.today )
    order_line_lines = fields.One2many('customer.order.line','order_id',string='Order Lines')
    total_amount = fields.Float(string='Total Amount',compute='_compute_amounts', store=True)
    paid_amount = fields.Float(string='Paid Amount',default=0.0)
    balance_amount = fields.Float(string='Balance Amount',compute='_compute_amounts',store=True)
    status = fields.Selection([('draft', 'Draft'),('confirmed', 'Confirmed'),('delivered', 'Delivered'),('cancelled', 'Cancelled'),],string='Status',default='draft',required=True)
    delivery_ids = fields.One2many('delivery.information','order_id',string='Deliveries')

    delivery_count = fields.Integer(string='Delivery Count',compute='_compute_delivery_count')
    total_quantity = fields.Float(string='Total Quantity',compute='_compute_total_quantity',store=True)
    production_ids = fields.One2many( 'production.information','customer_order_id',string='Productions')
    production_count = fields.Integer(string='Productions',compute='_compute_production_count')
    payment_method = fields.Selection([('online', 'Online Payment'),('bank', 'Bank Transfer'),('cod', 'Cash on Delivery'),],string='Payment Method',default='cod',required=True)
    payment_status = fields.Selection([('unpaid', 'Unpaid'),('partial', 'Partial'),('paid', 'Paid'),],string='Payment Status',compute='_compute_payment_status',store=True)

    # -----------------SEQUENCE------------------
    @api.model_create_multi
    def create(self, vals_list):
        print("========== CUSTOMER ORDER CREATE ==========")
        print("BEFORE:", vals_list)
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                name = self.env['ir.sequence'].next_by_code('customer.order.information')
                print("SEQUENCE GENERATED:", name)
                vals['name'] = name or 'New'
        print("AFTER:", vals_list)
        return super().create(vals_list)

#########
# compute fields
#########
    #------------------------ COMPUTE TOTAL + BALANCE------------------
    @api.depends('order_line_lines.subtotal', 'paid_amount')
    def _compute_amounts(self):
        for record in self:
            record.total_amount = sum(record.order_line_lines.mapped('subtotal'))
            record.balance_amount = (record.total_amount -record.paid_amount)

    # -----------------------COMPUTE PAYMENT STATUS----------------------
    @api.depends('paid_amount', 'total_amount')
    def _compute_payment_status(self):
        for record in self:
            if record.paid_amount <= 0:
                record.payment_status = 'unpaid'
            elif record.paid_amount < record.total_amount:
                record.payment_status = 'partial'
            else:
                record.payment_status = 'paid'

    @api.depends('delivery_ids')
    def _compute_delivery_count(self):
        for record in self:
            record.delivery_count = len(record.delivery_ids)

    @api.depends('order_line_lines.quantity')
    def _compute_total_quantity(self):
        for record in self:
            record.total_quantity = sum(record.order_line_lines.mapped('quantity'))

    @api.depends('production_ids')
    def _compute_production_count(self):
        for record in self:
            record.production_count = len(record.production_ids)


#########
# constrains
#########
    # -----------VALIDATE PAID AMOUNT----------------
    @api.constrains('paid_amount', 'total_amount')
    def _check_paid_amount(self):
        for record in self:
            if record.paid_amount < 0:
                raise ValidationError('Paid Amount cannot be negative.')
            if record.paid_amount > record.total_amount:
                raise ValidationError(
                    'Paid Amount cannot be greater than '
                    'Total Amount.'
                )
#########
# Button
#########
    # ----------CONFIRM--------------
    def action_confirm(self):
        for record in self:
            if record.status != 'draft':
                raise ValidationError('Only Draft orders can be confirmed.')
            if not record.order_line_lines:
                raise ValidationError(
                    'Add at least one order line '
                    'before confirmation.'
                )
            record.status = 'confirmed'
 
    # -----------MARK DELIVERED-----------
    def action_mark_delivered(self):
        for record in self:
            if record.status != 'confirmed':
                raise ValidationError(
                    'Only Confirmed orders can be '
                    'marked as Delivered.'
                )
            record.status = 'delivered'

    #-------------- CANCEL-----------------
    def action_cancel(self):
        for record in self:
            if record.status == 'delivered':
                raise ValidationError('Delivered order cannot be cancelled.')
            record.status = 'cancelled'

    # ----------------RESET TO DRAFT-----------------
    def action_reset_to_draft(self):
        for record in self:
            if record.status == 'delivered':
                raise ValidationError('Delivered order cannot be reset to Draft.')
            record.status = 'draft'

    def action_view_deliveries(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Deliveries',
            'res_model': 'delivery.information',
            'view_mode': 'list,form',
            'domain': [('order_id', '=', self.id)],
            'context': {
                'default_order_id': self.id,
            },
        }

    def action_view_productions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Productions',
            'res_model': 'production.information',
            'view_mode': 'list,form',
            'domain': [('customer_order_id', '=', self.id)],
            'context': {'default_customer_order_id': self.id
            },
        }
    
    def action_create_production(self):
        self.ensure_one()

        if self.status != 'confirmed':
            raise ValidationError('Only Confirmed orders can create production.')

        if not self.order_line_lines:
            raise ValidationError('Order must contain at least one order line.')
        if len(self.order_line_lines) > 1:
            raise ValidationError('Please create production separately for each order line.')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Production',
            'res_model': 'customer.order.production.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_order_line_id': self.order_line_lines[0].id,
            },
        }

    
# ------------CUSTOMER ORDER LINE---------------
class CustomerOrderLine(models.Model):

    _name = 'customer.order.line'
    _description = 'Customer Order Line'
    _rec_name = 'product_id'



    order_id = fields.Many2one('customer.order.information',string='Order',required=True,ondelete='cascade')
    product_id = fields.Many2one('pottery.product.information',string='Pottery Product',required=True,domain=[('active', '=', True)])
    # RELATED FIELD
    product_name = fields.Char(related='product_id.name',string='Product Name',readonly=True)
    quantity = fields.Float(string='Quantity',required=True,default=1.0)
    unit_price = fields.Float(string='Unit Price',required=True)
    subtotal = fields.Float(string='Subtotal',compute='_compute_subtotal',store=True)

#########
# compute fields
#########   
# -----------COMPUTE SUBTOTAL----------------
    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = (record.quantity *record.unit_price)

    #-----------------PRODUCT → UNIT PRICE-------------

#########
# onchange
######### 
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            if record.product_id:
                record.unit_price = (record.product_id.selling_price)

   
#########
# Constrain
######### 
 # -------------VALIDATION------------
    @api.constrains('quantity', 'unit_price')
    def _check_values(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError('Quantity must be greater than zero.')
            if record.unit_price < 0:
                raise ValidationError('Unit Price cannot be negative.')
    