{
    'name': 'Ouatation Management',
    'version': '1.0',
    'summary': """Summary of the Module""",
    'description': """Description of the Module""",
    'category': 'service',
    'author': 'Mouniga',
    'depends':['web','base'],
    'data':[
    	'security/ir.model.access.csv',
        'views/customer_information.xml',   
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}