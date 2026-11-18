# from odoo import http


# class CustomerReference(http.Controller):
#     @http.route('/customer_reference/customer_reference', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customer_reference/customer_reference/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('customer_reference.listing', {
#             'root': '/customer_reference/customer_reference',
#             'objects': http.request.env['customer_reference.customer_reference'].search([]),
#         })

#     @http.route('/customer_reference/customer_reference/objects/<model("customer_reference.customer_reference"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customer_reference.object', {
#             'object': obj
#         })

