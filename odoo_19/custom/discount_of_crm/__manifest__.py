{
    'name': 'Discount Of sale CRM',
    'version': '1.0',
    'summary': """Summary of the Module""",
    'description': """Description of the Module""",
    'category': 'service',
    'author': 'Mouniga',
    'depends':['crm','sale',],
    'data':[
        'views/lead_discount.xml',
        'views/sale_order.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}