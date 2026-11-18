{
    'name': 'Hospital Information System Integration',
    'version': '1.0',
    'summary': """hospital information system""",
    'description': """Hospital Information System Integration of the module""",
    'category': 'service',
    'author': 'Mouniga',
    'depends':['web','base','contacts','report_xlsx','mail',],
    'data':[
        'security/security.xml',
    	'security/ir.model.access.csv',


        'data/visit_sequence.xml',
        'data/patient_sequence.xml',
        'data/lab_result.xml',
        'data/mail_template.xml',
        'data/cron.xml',
        'data/email_template.xml',

        
        'views/hospital_patient_visit.xml',
        'views/hospital_lab_result.xml',
        'views/hospital_lab_test.xml',
        'views/hospital_department.xml',
        'views/hospital_doctor.xml',   
        'views/hospital_diagnosis.xml',
        'views/hospital_prescription.xml',              
        'views/res_partner.xml',
      

        'wizard/hospital_followup_wizard.xml',

        'report/lab_result_report.xml',
        'report/report_template.xml',
        'report/report_action.xml',
        'report/lab_result_action.xml',
        'report/lab_result_template.xml',
        'report/visit_report_template.xml',
        'report/visit_report_action.xml',
        'report/prescription_report_template.xml',
        'report/prescription_report_action.xml',
        'report/doctor_daily_report_template.xml',
        'report/doctor_daily_report_action.xml',

        
        
        
        
        
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}