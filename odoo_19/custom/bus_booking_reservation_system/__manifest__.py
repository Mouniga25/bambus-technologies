{
    'name': 'Bus Booking Reservation System',
    'version': '1.0',
    'summary': """Summary of the Module""",
    'description': """Description of the Module""",
    'category': 'service',
    'author': 'Mouniga',
    'depends':['web','base', 'website','report_xlsx'],
    'data':[
    	'security/ir.model.access.csv',
        'views/booking_forms.xml',
        'views/places_info.xml',
        'views/classof_service.xml',
        'views/booking_templates.xml',
        'report/report_action.xml',
        'report/report_template.xml',
        'report/bus_booking_report.xml',
        
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}