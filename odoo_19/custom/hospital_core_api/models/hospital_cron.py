from odoo import models, fields
from datetime import timedelta


class HospitalCron(models.Model):
    _name = "hospital.cron"
    _description = "Hospital Scheduled Actions"

                 
    def send_appointment_reminder(self):

        tomorrow = fields.Date.today() + timedelta(days=1)

        visits = self.env['hospital.patient.visit'].search([
            ('visit_date','>=',tomorrow),
            ('visit_date','<',tomorrow + timedelta(days=1))
        ])

        for visit in visits:

            template = self.env.ref(
                'hospital_core_api.appointment_reminder_mail'
            )

            template.send_mail(
                visit.id,
                force_send=True
            )


    def mark_overdue_lab_reports(self):

        limit_date = fields.Date.today() - timedelta(days=7)

        labs = self.env['hospital.lab.result'].search([
            ('amount_status','=','pending'),
            ('test_date','<',limit_date)
        ])

        for lab in labs:
            lab.amount_status = 'overdue'


    def archive_inactive_patients(self):

        limit_date = fields.Date.today() - timedelta(days=365)

        patients = self.env['res.partner'].search([
            ('is_patient','=',True),
            ('last_visit_date','<',limit_date)
        ])

        patients.write({
            'active':False
        })