# from odoo import http


# class CustomLeadToSale(http.Controller):
#     @http.route('/custom_lead_to_sale/custom_lead_to_sale', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_lead_to_sale/custom_lead_to_sale/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_lead_to_sale.listing', {
#             'root': '/custom_lead_to_sale/custom_lead_to_sale',
#             'objects': http.request.env['custom_lead_to_sale.custom_lead_to_sale'].search([]),
#         })

#     @http.route('/custom_lead_to_sale/custom_lead_to_sale/objects/<model("custom_lead_to_sale.custom_lead_to_sale"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_lead_to_sale.object', {
#             'object': obj
#         })

