# from odoo import http


# class VehicleRentalManagement(http.Controller):
#     @http.route('/vehicle_rental_management/vehicle_rental_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vehicle_rental_management/vehicle_rental_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vehicle_rental_management.listing', {
#             'root': '/vehicle_rental_management/vehicle_rental_management',
#             'objects': http.request.env['vehicle_rental_management.vehicle_rental_management'].search([]),
#         })

#     @http.route('/vehicle_rental_management/vehicle_rental_management/objects/<model("vehicle_rental_management.vehicle_rental_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vehicle_rental_management.object', {
#             'object': obj
#         })

