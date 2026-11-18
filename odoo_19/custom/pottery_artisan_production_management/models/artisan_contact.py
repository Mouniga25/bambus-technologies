from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Artisan Information
    is_artisan = fields.Boolean(string='Is Artisan',default=False)
    artisan_skill = fields.Char(string='Artisan Skill')
    artisan_experience = fields.Integer(string='Artisan Experience')
    artisan_type = fields.Selection([('full_time', 'Full Time'),('part_time', 'Part Time'),('contract', 'Contract'),],string='Artisan Type')
    customer_order_ids = fields.One2many('customer.order.information','customer_id',string='Customer Orders')
    customer_order_count = fields.Integer(string='Order Count',compute='_compute_customer_order_count')


#########
# compute fields
#########

    @api.depends('customer_order_ids')
    def _compute_customer_order_count(self):
        for record in self:
            record.customer_order_count = len(record.customer_order_ids)
    def action_view_customer_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Orders',
            'res_model': 'customer.order.information',
            'view_mode': 'list,form',
            'domain': [
                ('customer_id', '=', self.id)
            ],
            'context': {
                'default_customer_id': self.id
            },
        }
#########
# onchange
#########
    # ---------ARTISAN NAME VALIDATION----------
    @api.onchange("name")
    def onchange_artisan_name(self):
        for rec in self:
            if rec.is_artisan and rec.name:
                for value in rec.name:
                    if value.isdigit():
                        raise ValidationError("Artisan Name must contain letters only.")
                    
    # -------------ARTISAN PHONE VALIDATION------------
    @api.onchange("phone")
    def onchange_artisan_phone(self):
        for rec in self:
            if rec.is_artisan and rec.phone:
                if not rec.phone.isdigit():
                    raise ValidationError("Phone number must contain numbers only.")
                if len(rec.phone) != 10:
                    raise ValidationError("Phone number must contain exactly 10 digits.")

    # --------------ARTISAN EMAIL VALIDATION----------------
    @api.onchange("email")
    def onchange_email(self):
        for rec in self:
            if rec.is_artisan and rec.email:
                if '.com' not in rec.email or '@' not in rec.email:
                    raise ValidationError(
                        "Please enter a valid email format "
                        "like example@gmail.com"
                    )