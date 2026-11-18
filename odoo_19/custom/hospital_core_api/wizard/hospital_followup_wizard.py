from odoo import api, fields, models


class HospitalFollowupWizard(models.TransientModel):
    _name = 'hospital.followup.wizard'
    _description = "Hospital Followup Wizard"

    patient_id = fields.Many2one(
        'res.partner',
        string="Patient",
        required=True,
        domain=[("is_patient", "=", True)]
    )

    doctor_id = fields.Many2one(
        'hospital.doctor',
        string="Doctor Name"
    )

    appointment_date = fields.Datetime(
        string="Next Appointment",
        required=True
    )

    notes = fields.Text(
        string="Notes"
    )


    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        active_id = self.env.context.get('active_id')

        if active_id:
            visit = self.env['hospital.patient.visit'].browse(active_id)

            res['patient_id'] = visit.patient_id.id
            res['doctor_id'] = visit.doctor_id.id

            if visit.next_followup_date:
                res['appointment_date'] = fields.Datetime.to_datetime(
                    visit.next_followup_date
                )

            res['notes'] = visit.notes

        return res


    def action_schedule(self):

        self.env['hospital.patient.visit'].create({
            'patient_id': self.patient_id.id,
            'doctor_id': self.doctor_id.id,
            'visit_date': self.appointment_date,
            'notes': self.notes,
        })

        return {
            'type': 'ir.actions.act_window_close'
        }