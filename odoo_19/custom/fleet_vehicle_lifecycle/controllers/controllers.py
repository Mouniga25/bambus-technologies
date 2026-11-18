# from odoo import http


# class FleetVehicleLifecycle(http.Controller):
#     @http.route('/fleet_vehicle_lifecycle/fleet_vehicle_lifecycle', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fleet_vehicle_lifecycle/fleet_vehicle_lifecycle/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fleet_vehicle_lifecycle.listing', {
#             'root': '/fleet_vehicle_lifecycle/fleet_vehicle_lifecycle',
#             'objects': http.request.env['fleet_vehicle_lifecycle.fleet_vehicle_lifecycle'].search([]),
#         })

#     @http.route('/fleet_vehicle_lifecycle/fleet_vehicle_lifecycle/objects/<model("fleet_vehicle_lifecycle.fleet_vehicle_lifecycle"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fleet_vehicle_lifecycle.object', {
#             'object': obj
#         })

