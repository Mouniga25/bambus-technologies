# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Bus Booking Reservation System',
    'version': '1.0',
    'category': 'Service',
    'description': """Hello Evveryone...""",
    'depends':[
    'base', 
    'web',
    'report_xlsx',
    
    ],
    'data': [
   'security/ir.model.access.csv',
   'data/sequence_data.xml',
   'wizard/wizard_view.xml',
   'report/report_action.xml',
   'report/report_template.xml',
   'report/booking_xlsx.xml',
   'views/booking_info_view.xml',
   'views/class_of_service_view.xml',
   'views/place_view.xml',
  
   
   
],
     


       
       
       
       
    
 
    'installable': True,
    'application':True,
    'author': 'Ragul sekar',
    'license': 'LGPL-3',
}
