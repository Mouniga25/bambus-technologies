from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import qrcode
import base64
from io import BytesIO
import secrets



class HospitalPatientVisit(models.Model):
    _name = 'hospital.patient.visit'
    _description = "Hospital Patient Visit"
    _rec_name ="patient_id"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    #sequence
    visit_number = fields.Char(string="Visit Number",required=True, copy=False, readonly=True, default='New')
    

    #patient Detail
    patient_id = fields.Many2one('res.partner',string="Patient", required=True,domain =[("is_patient", "=", True)])
    doctor_id = fields.Many2one('hospital.doctor',string="Doctor Name")
    department_id = fields.Many2one('hospital.department',string="Department")
    visit_date = fields.Datetime(string="Visit Date", required=True)
    symptoms = fields.Char(string="Symptoms")
    diagnosis_id = fields.Many2one('hospital.diagnosis',string="Diagnosis")
    # prescription_id = fields.Many2one('hospital.prescription',string="Prescription", required=True)
    notes =  fields.Text(string="Notes", required=True)
    state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting'),('consultation', 'Consultation'), ('lab_requested', 'Lab Requested'), ('completed', 'Completed'), ('cancelled', 'Cancelled') ], default="draft")

    next_followup_date = fields.Date(string="Next Follow-up Date",compute="_compute_next_followup_date",store=True)
    qr_code = fields.Binary(string="QR Code")

    approval_token = fields.Char(string="Approval Token",copy=False,readonly=True,index=True,)

    departments_id = fields.Many2one(related="doctor_id.department_id",string="Department",store=True,readonly=True)
    reminder_sent = fields.Boolean(string="Reminder Sent",default=False)


    def get_approval_url(self):
        self.ensure_one()

        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url'
        )

        return f"{base_url}/hospital/appointment/approval/{self.approval_token}"

    
    """creating sequence number for the patient visit"""
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('visit_number', 'New') == 'New':
                vals['visit_number'] = self.env['ir.sequence'].next_by_code(
                    'hospital.patient.visit'
                ) or 'New'

            if not vals.get('approval_token'):
                vals['approval_token'] = secrets.token_urlsafe(32)   
        records = super().create(vals_list)

        for rec in records:
            rec.generate_qr_code()
        return records

    def generate_qr_code(self):
        for rec in self:

            data = f"""Hospital Visit Report

    Patient ID: {rec.patient_id.patient_number}
    Patient Name: {rec.patient_id.patient_name or rec.patient_id.name}
    Doctor Name: {rec.doctor_id.doctor_name}
    Department: {rec.department_id.department_name}
    Doctor Notes:
    {rec.notes}
    """
            qr = qrcode.QRCode(version=2,box_size=10,border=5)

            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black",back_color="white")

            buffer = BytesIO()
            img.save(buffer, format="PNG")

            rec.qr_code = base64.b64encode(
                buffer.getvalue()
            )
   
    # """Doctor and department"""
    # @api.onchange("doctor_id")
    # def onchange_doctor_id(self):
    #     if self.doctor_id:
    #         self.department_id = self.doctor_id.department_id
    #     else:
    #         self.department_id = False

    
#########
#ACTION
#########
    def action_draft(self):
        self.write({'state': 'draft'})
    def action_waiting(self):
        self.write({'state': 'waiting'})
    def action_consultation(self):
        print("========== CONSULTATION STARTED ==========")
        self.write({'state': 'consultation'})

        template = self.env.ref(
            'hospital_core_api.mail_template_appointment_confirmed',
            raise_if_not_found=False
        )
        print("CONFIRM TEMPLATE :", template)
        for rec in self:
            print("PATIENT :", rec.patient_id.name)
            print("EMAIL :", rec.patient_id.email)
            if not template:
                print("❌ CONFIRM TEMPLATE NOT FOUND")

            if not rec.patient_id.email:
                print("❌ PATIENT EMAIL NOT FOUND")

            if template and rec.patient_id.email:
                try:
                    mail_id = template.send_mail(
                        rec.id,
                        force_send=True,
                        email_values={
                            'email_to': rec.patient_id.email,
                        }
                    )
                    print("MAIL ID :", mail_id)
                    print("✅ CONFIRM MAIL SEND CALLED")

                except Exception as e:
                    print("❌ CONFIRM MAIL ERROR :", e)
                
    def action_lab_requested(self):
        self.write({'state': 'lab_requested'})
    # def action_completed(self):
    #     self.write({'state': 'completed'})

    
    def action_cancelled(self):
        self.write({'state': 'cancelled'})

        template = self.env.ref(
            'hospital_core_api.mail_template_appointment_rejected',
            raise_if_not_found=False
        )

        for rec in self:
            if template and rec.patient_id.email:
                template.send_mail(
                    rec.id,
                    force_send=True,
                    email_values={
                        'email_to': rec.patient_id.email,
                    }
                )

    """Doctor name is requried"""
    @api.constrains("doctor_id")
    def _check_doctor(self):
        for rec in self:
            if not rec.doctor_id:
                raise ValidationError("Doctor is requried to fill")

            
    @api.depends("visit_date")
    def _compute_next_followup_date(self):
        for rec in self:
            if rec.visit_date:
                days = 7
                rec.next_followup_date = fields.Date.add(rec.visit_date.date(),days=days)
            else:
                rec.next_followup_date = False
    

    """Visiting date cannot be below Date of Birth"""
    @api.constrains("visit_date","patient_id")
    def _check_visiting_date(self):
        for rec in self:
            if rec.patient_id.date_of_birth and rec.visit_date:
                if rec.visit_date.date() < rec.patient_id.date_of_birth:
                    raise ValidationError("Visit date cannot precede Date of Birth.")


#########
#cron
#########

    def send_appointment_reminder(self):
        print("========== CRON STARTED ==========")

        tomorrow = fields.Datetime.now().replace(
            hour=0,
            minute=0,
            second=0
        ) + relativedelta(days=1)

        tomorrow_end = tomorrow + relativedelta(days=1)
        print(tomorrow,"-------------",tomorrow_end)

        visits = self.search([
            # ('visit_date', '>=', tomorrow),
            # ('visit_date', '<', tomorrow_end),
            ('reminder_sent', '=', False)
        ])

        print("VISITS COUNT :", len(visits))

        template = self.env.ref(
            'hospital_core_api.mail_template_appointment_reminder',
            raise_if_not_found=False
        )

        if not template:
            print("MAIL TEMPLATE NOT FOUND")
            return

        print("MAIL TEMPLATE FOUND---------------------",visits)


        for visit in visits:

            print("--------PATIENT :", visit.patient_id.name)
            print("--------EMAIL :", visit.patient_id.email)

            if visit.patient_id.email:

                try:
                    print("TEMPLATE NAME :", template.name)
                    print("TEMPLATE SUBJECT :", repr(template.subject))
                    print("EMAIL FROM :", repr(template.email_from))
                    print("EMAIL TO :", repr(template.email_to))

                    mail_id = template.send_mail(
                        visit.id,
                        force_send=True,
                        email_values={
                            'email_to': visit.patient_id.email,
                        }
                    )

                    if mail_id:
                        visit.write({
                            'reminder_sent': True
                        })

                    print("MAIL ID :", mail_id)
                    print("MAIL SENT :", visit.patient_id.email)

                except Exception as e:
                    print("MAIL ERROR :", e)

            else:
                print(
                    "EMAIL NOT FOUND FOR :",
                    visit.patient_id.name
                )


    def action_open_followup_wizard(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Hospital Followup Wizard',
            'res_model': 'hospital.followup.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }

##########
#email - outgoing   action for completed and reply mail code 
#########
    def action_completed(self):
        self.write({'state': 'completed'})
        print("--------------completed__----------------")

        template = self.env.ref(
            'hospital_core_api.mail_template_appointment_completed',
            raise_if_not_found=False
        )

        print("TEMPLATE FOUND :", template)

        for rec in self:
            print("PATIENT :", rec.patient_id.name)
            print("EMAIL :", rec.patient_id.email)

            if template and rec.patient_id.email:
                mail_id = template.send_mail(
                    rec.id,
                    force_send=True,
                    email_values={
                        'email_to': rec.patient_id.email,  
                    }
                )

                rec.message_post(
                    body="Visit completed mail sent to patient.",
                    message_type="comment",
                    subtype_xmlid="mail.mt_comment"
                )
                # print("CREATED MAIL ID :", mail_id)

##########
#email - Incoming
#########  
    def message_new(self, msg_dict, custom_values=None):
        body = msg_dict.get('body')

        email = msg_dict.get('email_from')
        print("INCOMING MAIL FROM:", email)
        print("BODY:", body)
        patient_id = extract_from_body(body)
        patient = self.env['res.partner'].search([
            ('patient_id', '=', patient_id)
        ], limit=1)
        if patient:
            print("Existing Patient Found:", patient.name)
        else:
            print("New Patient Create")
        return super().message_new(
            msg_dict,
            custom_values
        )
  
    
    
     