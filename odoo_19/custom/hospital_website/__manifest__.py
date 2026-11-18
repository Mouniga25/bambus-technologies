{
    'name': 'Hospital Website',
    'version': '1.0',
    'summary': 'Hospital Website',
    'category': 'Website',
    'author': 'Mouniga',

    'depends': [
        'website',
        'hospital_core_api',
    ],

    'data': [
        'views/hospital_home.xml',
        'views/website_templates.xml',
        'views/my_appointments.xml',
        'views/appointment_approval.xml',
        'views/appointment_reschedule.xml',
        'views/appointment_action_success.xml',
    ],

    'installable': True,
    'application': True,
}