{
    'name': 'Dmart Management System',
    'version': '1.0',
    'summary': """Dmart Management System""",
    'description': """Dmart Management System of the module""",
    'category': 'service',  
    'author': 'Mouniga',
    'depends':['web','base',],
    'data':[
        
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/record_rule.xml',
        
    
        'views/bill_counter.xml',                 
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}