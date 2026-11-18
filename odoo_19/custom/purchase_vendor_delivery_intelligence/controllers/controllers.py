# from odoo import http


# class PurchaseVendorDeliveryIntelligence(http.Controller):
#     @http.route('/purchase_vendor_delivery_intelligence/purchase_vendor_delivery_intelligence', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_vendor_delivery_intelligence/purchase_vendor_delivery_intelligence/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_vendor_delivery_intelligence.listing', {
#             'root': '/purchase_vendor_delivery_intelligence/purchase_vendor_delivery_intelligence',
#             'objects': http.request.env['purchase_vendor_delivery_intelligence.purchase_vendor_delivery_intelligence'].search([]),
#         })

#     @http.route('/purchase_vendor_delivery_intelligence/purchase_vendor_delivery_intelligence/objects/<model("purchase_vendor_delivery_intelligence.purchase_vendor_delivery_intelligence"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_vendor_delivery_intelligence.object', {
#             'object': obj
#         })
