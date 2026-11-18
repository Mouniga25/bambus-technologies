from odoo import http
from odoo.http import request
from datetime import datetime


class HospitalWebsite(http.Controller):

    # =========================================================
    # HOME PAGE
    # =========================================================

    @http.route(
        '/hospital',
        type='http',
        auth='public',
        website=True
    )
    def hospital_home(self):

        return request.render(
            'hospital_website.hospital_home'
        )

    # =========================================================
    # APPOINTMENT PAGE
    # =========================================================

    @http.route(
        '/hospital/appointment',
        type='http',
        auth='public',
        website=True
    )
    def hospital_appointment(self):

        doctors = request.env[
            'hospital.doctor'
        ].sudo().search([])

        departments = request.env[
            'hospital.department'
        ].sudo().search([])

        return request.render(
            'hospital_website.hospital_appointment',
            {
                'doctors': doctors,
                'departments': departments,
            }
        )

    # =========================================================
    # APPOINTMENT SUBMIT
    # =========================================================

    @http.route(
        '/hospital/appointment/submit',
        type='http',
        auth='public',
        website=True,
        methods=['POST'],
        csrf=True
    )
    def hospital_appointment_submit(self, **post):

        # -----------------------------------------------------
        # 1. GET FORM VALUES
        # -----------------------------------------------------

        patient_name = post.get('patient_name')
        email = post.get('email')
        phone = post.get('phone')
        doctor_id = post.get('doctor_id')
        department_id = post.get('department_id')
        visit_date = post.get('visit_date')
        symptoms = post.get('symptoms')

        # -----------------------------------------------------
        # 2. CLEAN VALUES
        # -----------------------------------------------------

        patient_name = (patient_name or '').strip()
        email = (email or '').strip()
        phone = (phone or '').strip()
        symptoms = (symptoms or '').strip()

        # -----------------------------------------------------
        # 3. CONVERT DATETIME
        # -----------------------------------------------------

        if visit_date:

            visit_date = datetime.strptime(
                visit_date,
                '%Y-%m-%dT%H:%M'
            ).strftime(
                '%Y-%m-%d %H:%M:%S'
            )

        print(
            "---------- WEBSITE VISIT DATE ----------",
            visit_date
        )

        # -----------------------------------------------------
        # 4. FIND EXISTING PATIENT
        # -----------------------------------------------------

        Patient = request.env[
            'res.partner'
        ].sudo()

        patient = Patient.search([
            ('is_patient', '=', True),
            ('email', '=', email),
        ], limit=1)

        # -----------------------------------------------------
        # 5. CREATE PATIENT IF NOT EXISTS
        # -----------------------------------------------------

        if not patient:

            patient = Patient.create({

                'name': patient_name,

                'patient_name': patient_name,

                'email': email,

                'phone': phone,

                'is_patient': True,
            })

            print(
                "---------- NEW PATIENT CREATED ----------",
                patient
            )

        else:

            print(
                "---------- EXISTING PATIENT ----------",
                patient
            )

        # -----------------------------------------------------
        # 6. CREATE PATIENT VISIT
        # -----------------------------------------------------

        visit = request.env[
            'hospital.patient.visit'
        ].sudo().create({

            'patient_id': patient.id,

            'doctor_id':
                int(doctor_id)
                if doctor_id
                else False,

            'department_id':
                int(department_id)
                if department_id
                else False,

            'visit_date': visit_date,

            'symptoms': symptoms,

            'notes':
                'Appointment booked from website.',
        })

        print(
            "---------- CREATED VISIT ----------",
            visit
        )

        print(
            "---------- VISIT NUMBER ----------",
            visit.visit_number
        )

        print(
            "---------- APPROVAL TOKEN ----------",
            visit.approval_token
        )

        # =====================================================
        # 7. SEND APPOINTMENT REQUEST
        #    PATIENT -> HOSPITAL
        # =====================================================

        template = request.env.ref(
            'hospital_core_api.mail_template_appointment_request',
            raise_if_not_found=False
        )

        print(
            "---------- APPOINTMENT REQUEST TEMPLATE ----------",
            template
        )

        if template and patient.email:

            try:

                hospital_email = 'mouniga.k2512@gmail.com'

                mail_id = template.send_mail(
                    visit.id,
                    force_send=True,
                    email_values={

                        # Patient email -> From
                        'email_from': patient.email,

                        # Hospital email -> To
                        'email_to': hospital_email,

                        # Reply should go back to patient
                        'reply_to': patient.email,
                    }
                )

                print(
                    "---------- APPOINTMENT REQUEST MAIL SENT ----------"
                )

                print(
                    "---------- MAIL ID ----------",
                    mail_id
                )

                print(
                    "---------- FROM ----------",
                    patient.email
                )

                print(
                    "---------- TO ----------",
                    hospital_email
                )

            except Exception as e:

                print(
                    "---------- APPOINTMENT REQUEST MAIL ERROR ----------",
                    e
                )

        else:

            if not template:

                print(
                    "---------- APPOINTMENT REQUEST TEMPLATE NOT FOUND ----------"
                )

            if not patient.email:

                print(
                    "---------- PATIENT EMAIL NOT FOUND ----------"
                )

        # -----------------------------------------------------
        # 8. APPOINTMENT SUCCESS PAGE
        # -----------------------------------------------------

        return request.render(
            'hospital_website.hospital_appointment_success',
            {
                'visit': visit,
            }
        )

    # =========================================================
    # SECURE APPOINTMENT APPROVAL PAGE
    # =========================================================

    @http.route(
        '/hospital/appointment/approval/<string:token>',
        type='http',
        auth='public',
        website=True,
        methods=['GET']
    )
    def appointment_approval(self, token):

        print(
            "---------- APPROVAL PAGE TOKEN ----------",
            token
        )
        visit = request.env[
            'hospital.patient.visit'
        ].sudo().search([
            ('approval_token', '=', token),
        ], limit=1)
        if not visit:

            print(
                "---------- INVALID APPROVAL TOKEN ----------"
            )

            return request.not_found()

        print(
            "---------- APPROVAL VISIT ----------",
            visit.visit_number
        )

        # -----------------------------------------------------
        # RENDER APPROVAL PAGE
        # -----------------------------------------------------

        return request.render(
            'hospital_website.appointment_approval',
            {
                'visit': visit,
                'token': token,
            }
        )

    # =========================================================
    # CONFIRM APPOINTMENT
    # =========================================================

    @http.route(
        '/hospital/appointment/confirm/<string:token>',
        type='http',
        auth='public',
        website=True,
        methods=['POST'],
        csrf=True
    )
    def appointment_confirm(self, token):

        print(
            "---------- CONFIRM REQUEST ----------",
            token
        )

        # -----------------------------------------------------
        # FIND APPOINTMENT
        # -----------------------------------------------------

        visit = request.env[
            'hospital.patient.visit'
        ].sudo().search([
            ('approval_token', '=', token),
        ], limit=1)

        # -----------------------------------------------------
        # INVALID TOKEN
        # -----------------------------------------------------

        if not visit:

            print(
                "---------- INVALID TOKEN FOR CONFIRM ----------"
            )

            return request.not_found()

        # -----------------------------------------------------
        # CONFIRM
        #
        # Requirement:
        # Confirm -> state = completed
        # -----------------------------------------------------

        visit.sudo().write({
            'state': 'completed',
        })

        print(
            "---------- APPOINTMENT CONFIRMED ----------",
            visit.visit_number
        )

        print(
            "---------- STATE ----------",
            visit.state
        )

        # -----------------------------------------------------
        # SEND CONFIRMATION EMAIL TO PATIENT
        # -----------------------------------------------------

        template = request.env.ref(
            'hospital_core_api.mail_template_appointment_confirmed',
            raise_if_not_found=False
        )

        if template and visit.patient_id.email:

            try:

                mail_id = template.send_mail(
                    visit.id,
                    force_send=True,
                    email_values={
                        'email_to': visit.patient_id.email,
                    }
                )

                print(
                    "---------- CONFIRMATION MAIL SENT ----------",
                    mail_id
                )

            except Exception as e:

                print(
                    "---------- CONFIRMATION MAIL ERROR ----------",
                    e
                )

        # -----------------------------------------------------
        # SUCCESS PAGE
        # -----------------------------------------------------

        return request.render(
            'hospital_website.appointment_action_success',
            {
                'visit': visit,
                'action': 'confirmed',
            }
        )

    # =========================================================
    # REJECT APPOINTMENT
    # =========================================================

    @http.route(
        '/hospital/appointment/reject/<string:token>',
        type='http',
        auth='public',
        website=True,
        methods=['POST'],
        csrf=True
    )
    def appointment_reject(self, token):

        print(
            "---------- REJECT REQUEST ----------",
            token
        )

        # -----------------------------------------------------
        # FIND APPOINTMENT
        # -----------------------------------------------------

        visit = request.env[
            'hospital.patient.visit'
        ].sudo().search([
            ('approval_token', '=', token),
        ], limit=1)

        # -----------------------------------------------------
        # INVALID TOKEN
        # -----------------------------------------------------

        if not visit:

            print(
                "---------- INVALID TOKEN FOR REJECT ----------"
            )

            return request.not_found()

        # -----------------------------------------------------
        # REJECT
        #
        # Requirement:
        # Reject -> state = cancelled
        # My Appointments-la "Rejected" nu display pannalaam
        # -----------------------------------------------------

        visit.sudo().write({
            'state': 'cancelled',
        })

        print(
            "---------- APPOINTMENT REJECTED ----------",
            visit.visit_number
        )

        print(
            "---------- STATE ----------",
            visit.state
        )

        # -----------------------------------------------------
        # SEND REJECTION EMAIL TO PATIENT
        # -----------------------------------------------------

        template = request.env.ref(
            'hospital_core_api.mail_template_appointment_rejected',
            raise_if_not_found=False
        )

        if template and visit.patient_id.email:

            try:

                mail_id = template.send_mail(
                    visit.id,
                    force_send=True,
                    email_values={
                        'email_to': visit.patient_id.email,
                    }
                )

                print(
                    "---------- REJECTION MAIL SENT ----------",
                    mail_id
                )

            except Exception as e:

                print(
                    "---------- REJECTION MAIL ERROR ----------",
                    e
                )

        # -----------------------------------------------------
        # SUCCESS PAGE
        # -----------------------------------------------------

        return request.render(
            'hospital_website.appointment_action_success',
            {
                'visit': visit,
                'action': 'rejected',
            }
        )

    # =========================================================
    # RESCHEDULE PAGE
    # =========================================================

    @http.route(
        '/hospital/appointment/reschedule/<string:token>',
        type='http',
        auth='public',
        website=True,
        methods=['GET']
    )
    def appointment_reschedule(self, token):

        print(
            "---------- RESCHEDULE PAGE TOKEN ----------",
            token
        )

        # -----------------------------------------------------
        # FIND APPOINTMENT
        # -----------------------------------------------------

        visit = request.env[
            'hospital.patient.visit'
        ].sudo().search([
            ('approval_token', '=', token),
        ], limit=1)

        # -----------------------------------------------------
        # INVALID TOKEN
        # -----------------------------------------------------

        if not visit:

            print(
                "---------- INVALID TOKEN FOR RESCHEDULE ----------"
            )

            return request.not_found()

        # -----------------------------------------------------
        # RENDER NEXT FOLLOW-UP PAGE
        # -----------------------------------------------------

        return request.render(
            'hospital_website.appointment_reschedule',
            {
                'visit': visit,
                'token': token,
            }
        )

    # =========================================================
    # RESCHEDULE SUBMIT
    #
    # Reschedule-ku separate state illa.
    #
    # OLD APPOINTMENT
    #       ↓
    # cancelled
    #
    # NEW FOLLOW-UP APPOINTMENT
    #       ↓
    # draft / waiting
    #       ↓
    # My Appointments-la Pending
    # =========================================================

    @http.route(
        '/hospital/appointment/reschedule/submit/<string:token>',
        type='http',
        auth='public',
        website=True,
        methods=['POST'],
        csrf=True
    )
    def appointment_reschedule_submit(self, token, **post):

        print(
            "---------- RESCHEDULE SUBMIT ----------",
            token
        )

        # -----------------------------------------------------
        # FIND ORIGINAL APPOINTMENT
        # -----------------------------------------------------

        visit = request.env[
            'hospital.patient.visit'
        ].sudo().search([
            ('approval_token', '=', token),
        ], limit=1)

        # -----------------------------------------------------
        # INVALID TOKEN
        # -----------------------------------------------------

        if not visit:

            print(
                "---------- INVALID TOKEN FOR RESCHEDULE SUBMIT ----------"
            )

            return request.not_found()

        # -----------------------------------------------------
        # GET NEW APPOINTMENT DATE
        # -----------------------------------------------------

        appointment_date = post.get('appointment_date')

        if not appointment_date:

            return request.render(
                'hospital_website.appointment_reschedule',
                {
                    'visit': visit,
                    'token': token,
                    'error': 'Please select a new appointment date.',
                }
            )

        # -----------------------------------------------------
        # CONVERT DATETIME
        # -----------------------------------------------------

        try:

            appointment_date = datetime.strptime(
                appointment_date,
                '%Y-%m-%dT%H:%M'
            ).strftime(
                '%Y-%m-%d %H:%M:%S'
            )

        except ValueError:

            return request.render(
                'hospital_website.appointment_reschedule',
                {
                    'visit': visit,
                    'token': token,
                    'error': 'Invalid appointment date.',
                }
            )

        print(
            "---------- NEW FOLLOW-UP DATE ----------",
            appointment_date
        )

        # =====================================================
        # IMPORTANT
        # OLD APPOINTMENT = CANCELLED
        #
        # Separate "rescheduled" state add panna vendam.
        # Old appointment cancelled aagum.
        # =====================================================

        visit.sudo().write({
            'state': 'cancelled',
        })

        print(
            "---------- ORIGINAL APPOINTMENT CANCELLED ----------",
            visit.visit_number
        )

        print(
            "---------- ORIGINAL STATE ----------",
            visit.state
        )

        # =====================================================
        # CREATE NEXT FOLLOW-UP APPOINTMENT
        #
        # New visit default state model-la irukkum.
        # Usually draft / waiting.
        # My Appointments-la Pending-aa display pannalaam.
        # =====================================================

        new_visit = request.env[
            'hospital.patient.visit'
        ].sudo().create({

            'patient_id': visit.patient_id.id,

            'doctor_id': visit.doctor_id.id,

            'department_id': visit.department_id.id,

            'visit_date': appointment_date,

            'symptoms': visit.symptoms,

            'notes':
                'Next follow-up appointment created from reschedule.',
        })

        print(
            "---------- NEXT FOLLOW-UP CREATED ----------",
            new_visit
        )

        print(
            "---------- NEW VISIT NUMBER ----------",
            new_visit.visit_number
        )

        print(
            "---------- NEW FOLLOW-UP STATE ----------",
            new_visit.state
        )

        # -----------------------------------------------------
        # SEND RESCHEDULE EMAIL
        #
        # NOTE:
        # mail_template_appointment_rescheduled
        # must exist in hospital_core_api mail XML.
        # -----------------------------------------------------

        template = request.env.ref(
            'hospital_core_api.mail_template_appointment_rescheduled',
            raise_if_not_found=False
        )

        if template and visit.patient_id.email:

            try:

                mail_id = template.send_mail(
                    new_visit.id,
                    force_send=True,
                    email_values={
                        'email_to': visit.patient_id.email,
                    }
                )

                print(
                    "---------- RESCHEDULE MAIL SENT ----------",
                    mail_id
                )

            except Exception as e:

                print(
                    "---------- RESCHEDULE MAIL ERROR ----------",
                    e
                )

        else:

            if not template:

                print(
                    "---------- RESCHEDULE EMAIL TEMPLATE NOT FOUND ----------"
                )

            if not visit.patient_id.email:

                print(
                    "---------- PATIENT EMAIL NOT FOUND ----------"
                )

        # -----------------------------------------------------
        # SUCCESS PAGE
        # -----------------------------------------------------

        return request.render(
            'hospital_website.appointment_action_success',
            {
                'visit': new_visit,
                'action': 'rescheduled',
            }
        )

    # =========================================================
    # MY APPOINTMENTS
    # =========================================================

    @http.route(
        '/my/appointments',
        type='http',
        auth='user',
        website=True
    )
    def my_appointments(self):

        # -----------------------------------------------------
        # 1. GET LOGGED-IN USER EMAIL
        # -----------------------------------------------------

        user_email = request.env.user.email

        print(
            "---------- LOGGED USER ----------",
            request.env.user.name
        )

        print(
            "---------- LOGGED USER EMAIL ----------",
            user_email
        )

        # -----------------------------------------------------
        # 2. FIND PATIENT
        # -----------------------------------------------------

        patient = request.env[
            'res.partner'
        ].sudo().search([

            ('is_patient', '=', True),

            ('email', '=', user_email),

        ], limit=1)

        print(
            "---------- PATIENT FOUND ----------",
            patient
        )

        # -----------------------------------------------------
        # 3. PATIENT NOT FOUND
        # -----------------------------------------------------

        if not patient:

            return request.render(
                'hospital_website.my_appointments',
                {
                    'patient': False,
                    'visits': [],
                }
            )

        # -----------------------------------------------------
        # 4. GET PATIENT APPOINTMENTS
        # -----------------------------------------------------

        visits = request.env[
            'hospital.patient.visit'
        ].sudo().search([
            ('patient_id', '=', patient.id),
        ], order='visit_date desc')

        print(
            "---------- APPOINTMENTS FOUND ----------",
            len(visits)
        )

        # -----------------------------------------------------
        # 5. RENDER MY APPOINTMENTS
        # -----------------------------------------------------

        return request.render(
            'hospital_website.my_appointments',
            {
                'patient': patient,
                'visits': visits,
            }
        )