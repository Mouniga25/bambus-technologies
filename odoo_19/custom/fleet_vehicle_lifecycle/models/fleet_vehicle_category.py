from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FleetVehicleModelCategory(models.Model):
    _inherit = "fleet.vehicle.model.category"


    currency_id = fields.Many2one("res.currency",string="Currency",default=lambda self: self.env.company.currency_id.id,readonly=True,)
    max_recommended_age = fields.Integer(string="Maximum Recommended Age (Years)")
    max_recommended_odometer = fields.Integer(string="Maximum Recommended Odometer")
    annual_maintenance_budget = fields.Monetary(string="Annual Maintenance Budget",currency_field="currency_id")
    max_cost_per_km = fields.Monetary(string="Maximum Cost Per KM",currency_field="currency_id")
    major_repair_warning_count = fields.Integer(string="Major Repair Warning Count")



    @api.constrains("max_recommended_age","max_recommended_odometer","annual_maintenance_budget","max_cost_per_km","major_repair_warning_count",)
    def _check_positive_values(self):
        for rec in self:
            if rec.max_recommended_age < 0:
                raise ValidationError("Maximum Recommended Age cannot be negative.")

            if rec.max_recommended_odometer < 0:
                raise ValidationError("Maximum Recommended Odometer cannot be negative.")

            if rec.annual_maintenance_budget < 0:
                raise ValidationError("Annual Maintenance Budget cannot be negative.")

            if rec.max_cost_per_km < 0:
                raise ValidationError("Maximum Cost Per KM cannot be negative.")

            if rec.major_repair_warning_count < 0:
                raise ValidationError("Major Repair Warning Count cannot be negative.")