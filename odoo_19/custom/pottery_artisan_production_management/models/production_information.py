from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class ProductionInformation(models.Model):
    _name = 'production.information'
    _description = 'Production Information'
    _order = 'production_date desc'

    name = fields.Char(string='Production Reference',required=True,copy=False,readonly=True,default='New')
    product_id = fields.Many2one('pottery.product.information',string='Product',required=True, domain=[('active', '=', True)])
    artisan_id = fields.Many2one('village.artisan',string='Artisan',required=True, domain=[('active', '=', True)])
    quantity = fields.Float(string='Planned Quantity',required=True)
    required_clay = fields.Float(string='Required Clay (KG)',compute='_compute_required_clay',store=True)
    
    production_date = fields.Date(string='Production Date',required=True,default=fields.Date.today)
    status = fields.Selection([('draft', 'Draft'),('in_progress', 'In Production'),('drying', 'Drying'),('in_kiln', 'In Kiln'),('quality_check', 'Quality Check'),('completed', 'Completed'),], string='Status', default='draft', required=True)
    artisan_phone = fields.Char(related='artisan_id.phone',string='Artisan Phone',readonly=True)
    artisan_skill = fields.Char(related='artisan_id.skill',string='Artisan Skill',readonly=True)
    artisan_experience = fields.Integer(related='artisan_id.experience',string='Artisan Experience',readonly=True)

    produced_qty = fields.Float(string='Produced Quantity',default=0.0)
    rejected_qty = fields.Float(string='Rejected Quantity',default=0.0)
    passed_qty = fields.Float(string='Passed Quantity',compute='_compute_passed_qty',store=True)
    wastage_percentage = fields.Float(string='Wastage Percentage',compute='_compute_wastage_percentage',store=True)

    material_cost = fields.Float(string='Material Cost',compute='_compute_material_cost',store=True)
    labour_cost = fields.Float(string='Labour Cost',default=0.0)
    total_cost = fields.Float(string='Total Cost',compute='_compute_total_cost',store=True)

    raw_material_line = fields.One2many('production.raw.material.line','production_id',string='Raw Materials')
    is_delayed = fields.Boolean(string='Delayed',default=False,readonly=True)

    kiln_id = fields.Many2one('kiln.information',string='Kiln',domain="[('status', 'not in', ['maintenance', 'inactive'])]")
    kiln_type = fields.Selection(related='kiln_id.kiln_type',string='Kiln Type',readonly=True)
    kiln_capacity = fields.Float(related='kiln_id.capacity',string='Kiln Capacity',readonly=True)
    kiln_status = fields.Selection(related='kiln_id.status',string='Kiln Status',readonly=True)
    
    verification_url = fields.Char(string='Verification URL',compute='_compute_verification_url')
    quality_check_line = fields.One2many('quality.information','production_id',string='Quality Checks')
    quality_check_count = fields.Integer(string='Quality Checks',compute='_compute_quality_check_count')
    customer_order_id = fields.Many2one('customer.order.information',string='Customer Order',ondelete='restrict')
    drying_start_date = fields.Date(string='Drying Start Date')
    expected_drying_days = fields.Integer(string='Expected Drying Days',default=3)
    expected_drying_date = fields.Date(string='Expected Drying Date',compute='_compute_expected_drying_date',store=True)
    drying_notes = fields.Text(string='Drying Notes')

    recovery_required = fields.Boolean(string='Recovery Required',compute='_compute_recovery_required',store=True,readonly=True)
    pending_quantity = fields.Float(string='Pending Quantity',compute='_compute_pending_quantity',store=True)
    recovery_quantity = fields.Float(string='Recovery Quantity',default=0.0)
    recovery_passed_qty = fields.Float(string='Recovery Passed Quantity',default=0.0)
    final_good_qty = fields.Float(string='Final Good Quantity',compute='_compute_final_good_qty',store=True)
    recovery_status = fields.Selection([('not_required', 'Not Required'),('pending', 'Pending'),('in_progress', 'In Recovery'),('completed', 'Completed'),],string='Recovery Status',default='not_required')
    progress_percentage = fields.Float(string='Production Progress (%)',compute='_compute_progress_percentage',store=True)

    #-------------------Sequence----------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
        # Production Reference
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code(
                        'production.information'
                    ) or 'New'
                )
            # Automatically create Raw Materials
            product_id = vals.get('product_id')
            quantity = vals.get('quantity', 0)
            if product_id and quantity:
                product = self.env[
                    'pottery.product.information'
                ].browse(product_id)

                raw_material_lines = []

                for material_line in product.raw_material_lines:
                    raw_material_lines.append(
                        (0, 0, {
                            'raw_material_id': material_line.raw_material_id.id,
                            'required_quantity':
                                material_line.quantity_per_unit * quantity,
                        })
                    )

                vals['raw_material_line'] = raw_material_lines

        return super().create(vals_list)

#########
# compute fields
#########
    @api.depends('status')
    def _compute_progress_percentage(self):
        progress_map = {
            'draft': 0,
            'in_progress': 20,
            'drying': 40,
            'in_kiln': 60,
            'quality_check': 80,
            'completed': 100,
        }

        for record in self:
            record.progress_percentage = progress_map.get(
                record.status,
                0
            ) 
    @api.depends('passed_qty', 'recovery_passed_qty')
    def _compute_final_good_qty(self):
        for record in self:
            record.final_good_qty = (record.passed_qty +record.recovery_passed_qty)
    # Passed Quantity
    @api.depends('produced_qty','rejected_qty')
    def _compute_passed_qty(self):
        for record in self:
            record.passed_qty = (record.produced_qty- record.rejected_qty)

    # Wastage Percentage
    @api.depends('produced_qty','rejected_qty')
    def _compute_wastage_percentage(self):
        for record in self:
            if record.produced_qty:
                record.wastage_percentage = (record.rejected_qty/ record.produced_qty) * 100
            else:
                record.wastage_percentage = 0.0

    # Material Cost
    @api.depends('raw_material_line.material_cost')
    def _compute_material_cost(self):
        for record in self:
            record.material_cost = sum(record.raw_material_line.mapped('material_cost'))

    # Total Cost
    @api.depends('material_cost','labour_cost')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = (record.material_cost+ record.labour_cost)

    @api.depends('product_id', 'quantity')
    def _compute_required_clay(self):
        for record in self:
            if record.product_id and record.quantity:
                record.required_clay = (record.quantity *record.product_id.clay_required_per_unit)
            else:
                record.required_clay = 0.0

    @api.depends('quality_check_line')
    def _compute_quality_check_count(self):
        for record in self:
            record.quality_check_count = len(record.quality_check_line)
    @api.depends('drying_start_date', 'expected_drying_days')
    def _compute_expected_drying_date(self):
        for record in self:
            if record.drying_start_date and record.expected_drying_days:
                record.expected_drying_date = (
                    record.drying_start_date +
                    timedelta(days=record.expected_drying_days)
                )
            else:
                record.expected_drying_date = False

    @api.depends('customer_order_id','passed_qty','recovery_passed_qty')
    def _compute_pending_quantity(self):
        for record in self:
            if record.customer_order_id:
                order_qty = record.customer_order_id.total_quantity

                record.pending_quantity = max(order_qty - record.passed_qty - record.recovery_passed_qty,0.0)
            else:
                record.pending_quantity = 0.0


    @api.depends('customer_order_id','passed_qty','recovery_passed_qty')
    def _compute_pending_quantity(self):
        for record in self:
            if record.customer_order_id:
                order_qty = record.customer_order_id.total_quantity
                record.pending_quantity = max(order_qty- record.passed_qty- record.recovery_passed_qty,0.0)
            else:
                record.pending_quantity = 0.0
    @api.depends('customer_order_id', 'passed_qty')
    def _compute_recovery_required(self):
        for record in self:
            if record.customer_order_id:
                order_qty = record.customer_order_id.total_quantity

                record.recovery_required = (
                    record.passed_qty < order_qty
                )
            else:
                record.recovery_required = False

#########
# Default Get
#########
    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        vals['production_date'] = fields.Date.today()
        vals['status'] = 'draft'
        return vals

#########
# constrains
#########
    
    # Validations
    @api.constrains('quantity','produced_qty','rejected_qty','material_cost','labour_cost')
    def _check_values(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError('Planned Quantity must be greater than zero.' )
            
            if record.produced_qty < 0:
                raise ValidationError('Produced Quantity cannot be negative.' )
            
            if record.rejected_qty < 0:
                raise ValidationError('Rejected Quantity cannot be negative.')

            if record.rejected_qty > record.produced_qty:
                raise ValidationError('Rejected Quantity cannot be greater than Produced Quantity.')

            if record.material_cost < 0:
                raise ValidationError('Material Cost cannot be negative.')

            if record.labour_cost < 0:
                raise ValidationError('Labour Cost cannot be negative.')
    @api.constrains('kiln_id', 'quantity')
    def _check_kiln_assignment(self):
        for record in self:
            if not record.kiln_id:
                continue
    
            kiln = record.kiln_id
    
            if kiln.status == 'maintenance':
                raise ValidationError('Kiln is currently under maintenance and cannot be assigned.')
    
            if kiln.status == 'inactive':
                raise ValidationError('Inactive kiln cannot be assigned to a production.')
    
            if record.quantity > kiln.capacity:
                raise ValidationError(f'Production quantity ({record.quantity}) 'f'cannot exceed kiln capacity ({kiln.capacity}).')
#######
#BUTTON
######
    # Start Production
    def action_start_production(self):
        for record in self:

            # Check raw material stock
            for line in record.raw_material_line:
                available_qty = line.raw_material_id.available_quantity
                required_qty = line.required_quantity
    
                if available_qty < required_qty:
                    raise ValidationError(
                        f"Insufficient stock for {line.raw_material_id.name}. "
                        f"Available: {available_qty} "
                        f"{line.raw_material_id.unit}, "
                        f"Required: {required_qty} "
                        f"{line.raw_material_id.unit}."
                    )
            for line in record.raw_material_line:
                line.raw_material_id.available_quantity -= line.required_quantity
            # Start production
            if record.kiln_id:
                record.kiln_id.write({
                    'status': 'in_use'
                })

            record.status = 'in_progress'

    # Move to Drying
    def action_start_drying(self):
        for record in self:
            record.drying_start_date = fields.Date.today()
            record.status = 'drying'
    @api.depends('drying_start_date', 'expected_drying_days')
    def _compute_expected_drying_date(self):
        for record in self:
            if record.drying_start_date and record.expected_drying_days:
                record.expected_drying_date = (
                    record.drying_start_date +
                    timedelta(days=record.expected_drying_days)
                )
            else:
                record.expected_drying_date = False

    # Move to Kiln
    def action_start_kiln(self):
        for record in self:
            if record.status != 'drying':
                raise ValidationError('Production must be in Drying stage before starting Kiln.')
            if (record.expected_drying_date and fields.Date.today() < record.expected_drying_date):
                raise ValidationError(
                    f'Drying period is not completed. '
                    f'Expected drying date is '
                    f'{record.expected_drying_date.strftime("%d/%m/%Y")}.'
                )
            if not record.kiln_id:
                raise ValidationError('Please assign a Kiln before starting Kiln.')
            if record.kiln_id.status in ['maintenance', 'inactive']:
                raise ValidationError('This Kiln is not available for production.')
            if record.kiln_id.status == 'in_use':
                raise ValidationError('This Kiln is already in use.')
            if record.kiln_id.capacity < record.quantity:
                raise ValidationError('Kiln capacity is not sufficient for this production quantity.')
            record.status = 'in_kiln'
            record.kiln_id.status = 'in_use'


    def action_open_kiln_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assign Kiln',
            'res_model': 'production.kiln.wizard',
            'view_mode': 'form',  
            'target': 'new',
        }

    # Quality Check
    def action_quality_check(self):
        self.ensure_one()

        quality_record = self.env['quality.information'].create({
            'production_id': self.id,
            'inspector': self.env.user.id,
            'check_date': fields.Date.today(),
            'passed_qty': 0.0,
            'rejected_qty': 0.0,
        })

        self.status = 'quality_check'

        return {
            'type': 'ir.actions.act_window',
            'name': 'Quality Check',
            'res_model': 'quality.information',
            'view_mode': 'form',
            'res_id': quality_record.id,
            'target': 'current',
        }
    def action_view_quality_checks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quality Checks',
            'res_model': 'quality.information',
            'view_mode': 'list,form',
            'domain': [('production_id', '=', self.id)],
            'context': {'default_production_id': self.id,
            },
        }
    def action_check_recovery(self):
        for record in self:
            if record.pending_quantity > 0:
                record.recovery_required = True
                record.recovery_status = 'pending'
                record.recovery_quantity = record.pending_quantity
            else:
                record.recovery_required = False
                record.recovery_status = 'not_required'
                record.recovery_quantity = 0.0

    def action_start_recovery(self):
        for record in self:
            if not record.recovery_required:
                raise ValidationError('Recovery is not required for this production.')
            if record.recovery_status != 'pending':
                raise ValidationError('Recovery must be in Pending status before starting.')
            if record.pending_quantity <= 0:
                raise ValidationError('There is no pending quantity for recovery.')
            if record.recovery_quantity <= 0:
                raise ValidationError('Please enter Recovery Quantity before starting recovery.')
            if record.recovery_quantity > record.pending_quantity:
                raise ValidationError('Recovery Quantity cannot be greater than Pending Quantity.')

            record.recovery_status = 'in_progress'

    # =========================================================
    # COMPLETE RECOVERY
    # =========================================================
    def action_complete_recovery(self):
        for record in self:
            if record.recovery_status != 'in_progress':
                raise ValidationError('Recovery must be In Recovery before completing.')
            if record.recovery_quantity <= 0:
                raise ValidationError('Recovery Quantity must be greater than zero.')
            if record.recovery_passed_qty < 0:
                raise ValidationError('Recovery Passed Quantity cannot be negative.')
            if record.recovery_passed_qty > record.recovery_quantity:
                raise ValidationError('Recovery Passed Quantity cannot be greater than Recovery Quantity.')

            if record.recovery_passed_qty < record.recovery_quantity:
                raise ValidationError('All Recovery Quantity must pass quality check before completing recovery.')

            record.recovery_status = 'completed'
            record.recovery_required = False
    
    # Complete Production
    def action_complete_production(self):
        for record in self:
            if record.status != 'quality_check':
                raise ValidationError('Production must be in Quality Check stage before completion.')

            approved_quality = self.env['quality.information'].search([
                ('production_id', '=', record.id),
                ('status', '=', 'approved'),
            ], limit=1)
            if not approved_quality:
                raise ValidationError(
                    'Please approve the Quality Check before completing production.'
                )

            if record.produced_qty <= 0:
                raise ValidationError(
                    'Produced Quantity must be greater than zero.'
                )

            if record.final_good_qty <= 0:
                raise ValidationError(
                    'Final Good Quantity must be greater than zero.'
                )

            # Complete Production
            record.status = 'completed'

            # Make Kiln Available
            if record.kiln_id:
                record.kiln_id.write({
                    'status': 'available'
                })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Create Delivery',
                'res_model': 'delivery.creation.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_production_id': record.id,
                },
            }

        # =====================================================
        # CREATE DELIVERY AUTOMATICALLY
        # =====================================================

        if record.customer_order_id:

            existing_delivery = self.env[
                'delivery.information'
            ].search([
                ('order_id', '=', record.customer_order_id.id),
                ('status', '!=', 'cancelled'),
            ], limit=1)

            if not existing_delivery:

                self.env['delivery.information'].create({
                    'order_id': record.customer_order_id.id,
                    'quantity': record.final_good_qty,
                    'delivery_date': fields.Date.today(),
                })

    # Reset to Draft
    def action_reset_to_draft(self):
        for record in self:
            record.status = 'draft'

    # Prevent modification after completion
    def write(self, vals):
        active_statuses = ['in_progress','drying','in_kiln','quality_check',]
        for record in self:
            if record.status == 'completed':
                allowed_fields = {'status'}

                if set(vals.keys()) - allowed_fields:
                    raise ValidationError('Completed Production cannot be modified. ''Only an authorized user can reset it.' )

            # Check kiln assignment
            if vals.get('kiln_id'):

                kiln = self.env['kiln.information'].browse(vals['kiln_id'])
                # Maintenance kiln
                if kiln.status == 'maintenance':
                    raise ValidationError('Kiln is currently under maintenance ''and cannot be assigned.')

                # Inactive kiln
                if kiln.status == 'inactive':
                    raise ValidationError('Inactive kiln cannot be assigned to a production.')

                # Capacity validation
                if record.quantity > kiln.capacity:
                    raise ValidationError(f'Production quantity ({record.quantity}) 'f'cannot exceed kiln capacity ({kiln.capacity}).')

                # Busy kiln validation
                if kiln.status == 'in_use':

                    existing_production = self.search([('kiln_id', '=', kiln.id),('id', '!=', record.id),('status', 'in', active_statuses),], limit=1)

                    if existing_production:
                        raise ValidationError('This kiln is already busy and cannot be ' 'assigned to another active production.')

        return super().write(vals)

    # Prevent deletion after completion
    def unlink(self):
        for record in self:
            if record.status != 'draft':
                raise ValidationError('Completed Production cannot be deleted.')
        return super().unlink()

    

    @api.model
    def _cron_check_delayed_productions(self):
        limit_date = fields.Date.today() - timedelta(days=3)

        delayed_productions = self.search([('status', '=', 'in_progress'),('production_date', '<', limit_date),])
        all_in_progress = self.search([('status', '=', 'in_progress'),])
        all_in_progress.write({'is_delayed': False})
        delayed_productions.write({'is_delayed': True})
        return delayed_productions

    def _compute_verification_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.verification_url = ("{base_url}/production/verify/{record.id}")

    @api.onchange('product_id', 'quantity')
    def _onchange_product_id(self):
        for record in self:

            if not record.product_id:
                record.raw_material_line = [(5, 0, 0)]
                continue

            lines = [(5, 0, 0)]

            for material_line in record.product_id.raw_material_lines:
                lines.append((0, 0, {
                    'raw_material_id': material_line.raw_material_id.id,
                    'required_quantity': (
                        material_line.quantity_per_unit * record.quantity
                    ),
                }))

            record.raw_material_line = lines

class ProductionRawMaterialLine(models.Model):
    _name = 'production.raw.material.line'
    _description = 'Production Raw Material Line'

    production_id = fields.Many2one('production.information',string='Production',required=True,ondelete='cascade')
    raw_material_id = fields.Many2one('raw.material.information',string='Raw Material',required=True,domain=[('active', '=', True)])
    required_quantity = fields.Float(string='Required Quantity',required=True,default=1.0)
    unit_cost = fields.Float(string='Unit Cost',related='raw_material_id.unit_cost',readonly=True)
    material_cost = fields.Float(string='Material Cost',compute='_compute_material_cost',store=True)

    # Material Cost Calculation
    @api.depends('required_quantity', 'unit_cost')
    def _compute_material_cost(self):
        for record in self:
            record.material_cost = (record.required_quantity * record.unit_cost)

     # Required Quantity Validation
    @api.constrains('required_quantity')
    def _check_required_quantity(self):
        for record in self:
            if record.required_quantity <= 0:
                raise ValidationError('Required Quantity must be greater than zero.')



class ProductRawMaterialLine(models.Model):
    _name = 'product.raw.material.line'
    _description = 'Product Raw Material Line'

    product_id = fields.Many2one('pottery.product.information',string='Product',required=True,ondelete='cascade')
    raw_material_id = fields.Many2one('raw.material.information',string='Raw Material',required=True,domain=[('active', '=', True)])
    quantity_per_unit = fields.Float(string='Quantity Per Unit',required=True,default=1.0)
    unit = fields.Selection(related='raw_material_id.unit',string='Unit',readonly=True)
    unit_cost = fields.Float(related='raw_material_id.unit_cost',string='Unit Cost',readonly=True)
    material_cost_per_unit = fields.Float(string='Material Cost / Unit',compute='_compute_material_cost_per_unit',store=True)

    @api.depends('quantity_per_unit', 'unit_cost')
    def _compute_material_cost_per_unit(self):
        for record in self:
            record.material_cost_per_unit = (
                record.quantity_per_unit * record.unit_cost
            )

    @api.constrains('quantity_per_unit')
    def _check_quantity_per_unit(self):
        for record in self:
            if record.quantity_per_unit <= 0:
                raise ValidationError(
                    'Quantity Per Unit must be greater than zero.'
                )


    