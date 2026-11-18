{
    'name': 'Odoo Testing Demo',
    'version': '1.0',
    'summary': """Demo module for learning Odoo automated testing""",
    'description': """ Odoo Testing Demo
=================
This module is created only for learning Odoo automated testing.""",
    'category': 'Testing',
    'author': 'Mouniga',
    'depends':['base'],
    'data':[
         'security/ir.model.access.csv',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}