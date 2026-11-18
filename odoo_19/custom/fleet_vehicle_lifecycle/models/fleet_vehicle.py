from datetime import date

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"


    vehicle_age = fields.Integer(string="Vehicle Age",compute="_compute_vehicle_age",store=True,)
    age_usage_percentage = fields.Float(string="Age Usage Percentage",compute="_compute_age_usage_percentage",store=True,)
    budget_usage_percentage = fields.Float(string="Budget Usage Percentage",compute="_compute_budget_usage_percentage",store=True,)
    odometer_usage_percentage = fields.Float(string="Odometer Usage Percentage",compute="_compute_odometer_usage_percentage",store=True,)
    lifetime_service_cost = fields.Monetary(string="Lifetime Service Cost",currency_field="currency_id",compute="_compute_lifetime_service_cost",store=True,)
    current_year_service_cost = fields.Monetary(string="Current Year Service Cost",currency_field="currency_id",compute="_compute_current_year_service_cost",store=True,)
    previous_year_service_cost = fields.Monetary(string="Previous Year Service Cost",currency_field="currency_id",compute="_compute_previous_year_service_cost",store=True,)
    maintenance_cost_change_percentage = fields.Float(string="Maintenance Cost Change %",compute="_compute_maintenance_cost_change_percentage",store=True,)
    average_annual_maintenance_cost = fields.Monetary(string="Average Annual Maintenance Cost",currency_field="currency_id",compute="_compute_average_annual_maintenance_cost",store=True,)
    maintenance_cost_per_km = fields.Float(string="Maintenance Cost Per KM",compute="_compute_maintenance_cost_per_km",store=True,)
    cost_per_km_usage_percentage = fields.Float(string="Cost Per KM Usage Percentage",compute="_compute_cost_per_km_usage_percentage",store=True,)
    major_repair_count = fields.Integer(string="Major Repair Count",compute="_compute_major_repair_count",store=True,)
    lifecycle_status = fields.Selection([("healthy", "Healthy"),
            ("monitor", "Monitor"),
            ("review", "Replacement Review"),
            ("replace", "Replacement Recommended"),
        ],string="Lifecycle Status",compute="_compute_lifecycle_status",store=True,)
    replacement_reason = fields.Text(string="Replacement Reason",compute="_compute_lifecycle_status",store=True,)

    # =================================
    # Vehicle Age
    # =================================
    @api.depends("acquisition_date")
    def _compute_vehicle_age(self):
        today = date.today()

        for rec in self:
            if rec.acquisition_date:
                years = today.year - rec.acquisition_date.year

                if (today.month, today.day) < (
                    rec.acquisition_date.month,
                    rec.acquisition_date.day,
                ):
                    years -= 1

                rec.vehicle_age = years
            else:
                rec.vehicle_age = 0

    @api.constrains("acquisition_date")
    def _check_acquisition_date(self):
        today = fields.Date.today()
        for rec in self:
            if rec.acquisition_date and rec.acquisition_date > today:
                raise ValidationError(
                    "Acquisition Date cannot be in the future."
                )

    @api.constrains("order_date", "acquisition_date")
    def _check_registration_date(self):
        for rec in self:
            if (
                rec.order_date
                and rec.acquisition_date
                and rec.acquisition_date < rec.order_date
            ):
                raise ValidationError(
                    "Registration Date cannot be earlier than Order Date."
                )

    # =================================
    # Age Usage %
    # =================================
    @api.depends("vehicle_age", "category_id.max_recommended_age")
    def _compute_age_usage_percentage(self):
        for rec in self:
            if rec.category_id.max_recommended_age:
                rec.age_usage_percentage = (
                    rec.vehicle_age / rec.category_id.max_recommended_age
                ) * 100
            else:
                rec.age_usage_percentage = 0

    # =================================
    # Budget Usage %
    # =================================
    @api.depends(
        "current_year_service_cost",
        "category_id.annual_maintenance_budget",
    )
    def _compute_budget_usage_percentage(self):
        for rec in self:
            budget = rec.category_id.annual_maintenance_budget or 0

            if budget > 0:
                rec.budget_usage_percentage = (
                    rec.current_year_service_cost / budget
                ) * 100
            else:
                rec.budget_usage_percentage = 0

    # =================================
    # Odometer Usage %
    # =================================
    @api.depends("category_id.max_recommended_odometer")
    def _compute_odometer_usage_percentage(self):

        odometer_data = self.env["fleet.vehicle.odometer"]._read_group(
            [("vehicle_id", "in", self.ids),            
             ("vehicle_id.company_id", "in", self.mapped("company_id").ids)],
            ["vehicle_id"],
            ["value:max"],
        )

        odometer_map = {
            vehicle.id: value
            for vehicle, value in odometer_data
        }

        for rec in self:
            max_odo = rec.category_id.max_recommended_odometer or 0
            current_odo = odometer_map.get(rec.id, 0)

            if max_odo:
                rec.odometer_usage_percentage = (
                    current_odo / max_odo
                ) * 100
            else:
                rec.odometer_usage_percentage = 0

    # =================================
    # Lifetime Service Cost
    # =================================
    @api.depends("log_services.amount","log_services.service_type_id.consider_for_replacement",)
    def _compute_lifetime_service_cost(self):

        data = self.env["fleet.vehicle.log.services"]._read_group(
            [("vehicle_id", "in", self.ids),
             ("vehicle_id.company_id", "in", self.mapped("company_id").ids),
             ("service_type_id.consider_for_replacement", "=", True),],
            ["vehicle_id"],
            ["amount:sum"],
        )

        total_map = {vehicle.id: amount for vehicle, amount in data}

        for rec in self:
            rec.lifetime_service_cost = total_map.get(rec.id, 0)

    # =================================
    # Current Year Service Cost
    # =================================
    @api.depends("log_services.amount", "log_services.date")
    def _compute_current_year_service_cost(self):
        current_year = fields.Date.today().year

        for rec in self:
            total = 0

            for service in rec.log_services:
                if service.date:
                    service_date = fields.Date.to_date(service.date)

                    if service_date.year == current_year:
                        total += service.amount

            rec.current_year_service_cost = total

    # =================================
    # Previous Year Service Cost
    #=================================
    @api.depends("log_services.amount", "log_services.date")
    def _compute_previous_year_service_cost(self):
        previous_year = date.today().year - 1

        for rec in self:
            total = 0

            for service in rec.log_services:
                if service.date:
                    service_date = fields.Date.to_date(service.date)

                    if service_date.year == previous_year:
                        total += service.amount

            rec.previous_year_service_cost = total

    # =================================
    # Requirement 15
    # Maintenance Cost Change %
    # =================================
    @api.depends(
        "current_year_service_cost",
        "previous_year_service_cost",
    )
    def _compute_maintenance_cost_change_percentage(self):
        for rec in self:
            if rec.previous_year_service_cost > 0:
                rec.maintenance_cost_change_percentage = (
                    (
                        rec.current_year_service_cost
                        - rec.previous_year_service_cost
                    )
                    / rec.previous_year_service_cost
                ) * 100
            else:
                rec.maintenance_cost_change_percentage = 0

    # =================================
    # Average Annual Maintenance Cost
    # =================================
    @api.depends("lifetime_service_cost", "vehicle_age")
    def _compute_average_annual_maintenance_cost(self):
        for rec in self:
            if rec.vehicle_age > 0:
                rec.average_annual_maintenance_cost = (
                    rec.lifetime_service_cost / rec.vehicle_age
                )
            else:
                rec.average_annual_maintenance_cost = 0

    # =================================
    # Maintenance Cost Per KM
    # =================================
    @api.depends("lifetime_service_cost")
    def _compute_maintenance_cost_per_km(self):

        odometer_data = self.env["fleet.vehicle.odometer"]._read_group(
            [("vehicle_id", "in", self.ids),
             ("vehicle_id.company_id", "in", self.mapped("company_id").ids),],
            ["vehicle_id"],
            ["value:max"],
        )

        odometer_map = {
            vehicle.id: value
            for vehicle, value in odometer_data
        }

        for rec in self:
            current_odo = odometer_map.get(rec.id, 0)

            if current_odo > 0:
                rec.maintenance_cost_per_km = (
                    rec.lifetime_service_cost / current_odo
                )
            else:
                rec.maintenance_cost_per_km = 0

    # =================================
    # Cost Per KM Usage %
    # =================================
    @api.depends(
        "maintenance_cost_per_km",
        "category_id.max_cost_per_km",
    )
    def _compute_cost_per_km_usage_percentage(self):
        for rec in self:
            max_cost = rec.category_id.max_cost_per_km or 0

            if max_cost > 0:
                rec.cost_per_km_usage_percentage = (
                    rec.maintenance_cost_per_km / max_cost
                ) * 100
            else:
                rec.cost_per_km_usage_percentage = 0

    # =================================
    # Major Repair Count
    # Requirement 14 + Requirement 30
    # =================================
    @api.depends("log_services.service_type_id.cost_classification")
    def _compute_major_repair_count(self):

        data = self.env["fleet.vehicle.log.services"]._read_group(
            [
                ("vehicle_id", "in", self.ids),
                ("vehicle_id.company_id", "in", self.mapped("company_id").ids),
                ("service_type_id.cost_classification", "=", "major"),
            ],
            ["vehicle_id"],
            ["__count"],
        )

        count_map = {
            vehicle.id: count
            for vehicle, count in data
        }

        for rec in self:
            rec.major_repair_count = count_map.get(rec.id, 0)

    # =================================
    # Lifecycle Status
    # Requirement 10,11,12,13
    # =================================
    @api.depends(
        "age_usage_percentage",
        "odometer_usage_percentage",
        "budget_usage_percentage",
        "cost_per_km_usage_percentage",
        "major_repair_count",
        "category_id.major_repair_warning_count",
    )
    def _compute_lifecycle_status(self):
        for rec in self:

            reasons = []
            exceeded = 0

            # Age
            if rec.age_usage_percentage >= 100:
                exceeded += 1
                reasons.append("Recommended age exceeded")

            # Odometer
            if rec.odometer_usage_percentage >= 100:
                exceeded += 1
                reasons.append("Recommended odometer exceeded")

            # Budget
            if rec.budget_usage_percentage >= 100:
                exceeded += 1
                reasons.append("Annual maintenance budget exceeded")

            # Cost per KM
            if rec.cost_per_km_usage_percentage >= 100:
                exceeded += 1
                reasons.append("Maximum cost per KM exceeded")

            # Major Repairs
            if (
                rec.category_id.major_repair_warning_count
                and rec.major_repair_count >= rec.category_id.major_repair_warning_count
            ):
                exceeded += 1
                reasons.append("Major repair warning count reached")

            if exceeded >= 2:
                rec.lifecycle_status = "replace"

            elif exceeded == 1:
                rec.lifecycle_status = "review"

            elif (
                rec.age_usage_percentage >= 70
                or rec.odometer_usage_percentage >= 70
                or rec.budget_usage_percentage >= 80
            ):
                rec.lifecycle_status = "monitor"

            else:
                rec.lifecycle_status = "healthy"

            rec.replacement_reason = "; ".join(reasons)

    # =================================
    # Requirement 20
    # Major Repairs Smart Button
    # =================================
    def action_view_major_repairs(self):
        self.ensure_one()

        # Force recompute count
        self._compute_major_repair_count()

        return {
            "type": "ir.actions.act_window",
            "name": "Major Repairs",
            "res_model": "fleet.vehicle.log.services",
            "view_mode": "list,form",
            "domain": [
                ("vehicle_id", "=", self.id),
                ("service_type_id.cost_classification", "=", "major"),
            ],
            "context": {
                "default_vehicle_id": self.id,
            },
        }


    # =================================
    # Requirement 21
    # Maintenance Cost Smart Button
    # =================================
    def action_view_maintenance_cost(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Maintenance Cost",
            "res_model": "fleet.vehicle.log.services",
            "view_mode": "list,form",
            "domain": [
                ("vehicle_id", "=", self.id),
                ("service_type_id.consider_for_replacement", "=", True),
            ],
            "context": {
                "default_vehicle_id": self.id,
            },
        }

    # =================================
    # Requirement 22, 23 & 24
    # Monthly Fleet Lifecycle Review
    # =================================
    def cron_monthly_lifecycle_review(self):
        print("===== FLEET LIFECYCLE CRON STARTED =====")

        activity_type = self.env.ref("mail.mail_activity_data_todo")
        model_id = self.env["ir.model"]._get_id("fleet.vehicle")

        
        vehicles = self.search([("company_id", "in", self.env.companies.ids),])

        for vehicle in vehicles:

            if not vehicle.manager_id:
                continue

            # Existing lifecycle activity
            activity = self.env["mail.activity"].search([
                ("res_model_id", "=", model_id),
                ("res_id", "=", vehicle.id),
                ("activity_type_id", "=", activity_type.id),
                ("user_id", "=", vehicle.manager_id.id),
            ], limit=1)


            # Review / Replace vehicles mattum process pannum
            if vehicle.lifecycle_status in ["healthy", "monitor"]:
                if activity:
                    activity.action_done()
                continue

            note = (
                f"Vehicle '{vehicle.display_name}' requires lifecycle review.\n\n"
                f"Status: {vehicle.lifecycle_status}\n"
                f"Reason: {vehicle.replacement_reason or 'No reason available'}"
            )

            if activity:
                # Requirement 24 - Existing activity update
                activity.write({
                    "summary": "Monthly Fleet Lifecycle Review",
                    "note": note,
                })
            else:
                # Requirement 22 - Create new activity
                self.env["mail.activity"].create({
                    "res_model_id": model_id,
                    "res_id": vehicle.id,
                    "activity_type_id": activity_type.id,
                    "user_id": vehicle.manager_id.id,
                    "summary": "Monthly Fleet Lifecycle Review",
                    "note": note,
                })
            print(
                vehicle.display_name,
                vehicle.id,
                vehicle.lifecycle_status,
                vehicle.manager_id.name if vehicle.manager_id else "No Manager",)

  
    def cron_monthly_lifecycle_review(self):
        print("===== FLEET LIFECYCLE CRON STARTED =====")

        activity_type = self.env.ref("mail.mail_activity_data_todo")
        model_id = self.env["ir.model"]._get_id("fleet.vehicle")

        vehicles = self.search([("company_id", "in", self.env.companies.ids)])

        for vehicle in vehicles:

            print(
                f"Vehicle={vehicle.display_name}, "
                f"Status={vehicle.lifecycle_status}, "
                f"Manager={vehicle.manager_id.name if vehicle.manager_id else 'None'}")

            if not vehicle.manager_id:
                print("SKIP - No Manager")
                continue

            activity = self.env["mail.activity"].search([
                ("res_model_id", "=", model_id),
                ("res_id", "=", vehicle.id),
                ("activity_type_id", "=", activity_type.id),
                ("user_id", "=", vehicle.manager_id.id),
            ], limit=1)

            if vehicle.lifecycle_status in ["healthy", "monitor"]:
                print("===================SKIP - Healthy/Monitor============")
                if activity:
                    activity.action_done()
                continue

            note = (
                f"Vehicle '{vehicle.display_name}' requires lifecycle review.\n\n"
                f"Status: {vehicle.lifecycle_status}\n"
                f"Reason: {vehicle.replacement_reason or 'No reason available'}"
            )

            if activity:
                print("===================Updating existing activity===============")
                activity.write({
                    "summary": "Monthly Fleet Lifecycle Review",
                    "note": note,
                })
            else:
                print("Creating new activity")
                self.env["mail.activity"].create({
                    "res_model_id": model_id,
                    "res_id": vehicle.id,
                    "activity_type_id": activity_type.id,
                    "user_id": vehicle.manager_id.id,
                    "summary": "Monthly Fleet Lifecycle Review",
                    "note": note,
                })