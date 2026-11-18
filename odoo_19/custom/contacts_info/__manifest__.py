{
    'name': 'Contract Information',
    'version': '1.0',
    'summary': """contract information""",
    'description': """contract information of the module""",
    'category': 'service',
    'author': 'Mouniga',
    'depends':['web','base','contacts','contacts_info'],
    'data':[
    	'security/ir.model.access.csv',

        'data/patient_sequence.xml',
        'views/res_partner.xml',
           
        
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}