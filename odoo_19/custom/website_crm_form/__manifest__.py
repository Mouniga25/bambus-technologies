{
    'name': 'Website CRM Form',
    'version': '1.0',
    'summary': """Dmart Management System""",
    'description': """Dmart Management System of the module""",
    'category': 'service',
    'author': 'Mouniga',
    'depends':['website','crm',],
    'data':[
        'data/sequence.xml',
        'views/thank_you.xml',
        'views/website_form.xml',
        'views/crm_lead_views.xml',              
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}