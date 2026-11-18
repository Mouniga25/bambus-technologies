from odoo import http
from odoo.http import request


class PotteryWebsite(http.Controller):
    # =========================================================
    # WEBSITE HOME
    # =========================================================
    @http.route(
        '/pottery',
        type='http',
        auth='public',
        website=True
    )
    def pottery_home(self):
        products = request.env[
            'pottery.product.information'
        ].sudo().search([
            ('active', '=', True)
        ], limit=6)
        return request.render(
            'pottery_artisan_production_management.website_home',
            {
                'products': products,
            }
        )
    # =========================================================
    # PRODUCT DETAIL
    # =========================================================
    @http.route(
        '/pottery/product/<int:product_id>',
        type='http',
        auth='public',
        website=True
    )
    def pottery_product_detail(self, product_id):
        product = request.env[
            'pottery.product.information'
        ].sudo().browse(product_id)

        if not product.exists() or not product.active:
            return request.not_found()
        return request.render(
            'pottery_artisan_production_management.website_product_detail',
            {
                'product': product,
            }
        )
    # =========================================================
    # ORDER FORM
    # =========================================================
    @http.route(
        '/pottery/order',
        type='http',
        auth='public',
        website=True
    )
    def pottery_order_form(self, product_id=None, **kwargs):
        product = False
        if product_id:
            product = request.env[
                'pottery.product.information'
            ].sudo().browse(int(product_id))
            if not product.exists() or not product.active:
                return request.not_found()
        return request.render(
            'pottery_artisan_production_management.website_order_form',
            {
                'product': product,
            }
        )
    # =========================================================
    # SUBMIT ORDER
    # =========================================================
    @http.route(
        '/pottery/order/submit',
        type='http',
        auth='public',
        website=True,
        methods=['POST']
    )
    def pottery_order_submit(self, **post):
        # =====================================================
        # GET FORM VALUES
        # =====================================================
        product_id = post.get('product_id')
        quantity = float(post.get('quantity', 1))
        customer_name = post.get('customer_name')
        phone = post.get('phone')
        email = post.get('email')
        address = post.get('address')
        # =====================================================
        # VALIDATE QUANTITY
        # =====================================================
        if quantity <= 0:
            return request.not_found()
        # =====================================================
        # GET PRODUCT
        # =====================================================
        product = request.env[
            'pottery.product.information'
        ].sudo().browse(int(product_id))
        if not product.exists() or not product.active:
            return request.not_found()
        # =====================================================
        # FIND EXISTING CUSTOMER
        # =====================================================
        customer = request.env[
            'res.partner'
        ].sudo().search([
            ('email', '=', email)
        ], limit=1)
        # =====================================================
        # CREATE CUSTOMER IF NOT EXISTS
        # =====================================================
        if not customer:
            customer = request.env[
                'res.partner'
            ].sudo().create({
                'name': customer_name,
                'phone': phone,
                'email': email,
                'street': address,
            })
        # =====================================================
        # CREATE CUSTOMER ORDER
        # =====================================================
        order = request.env[
            'customer.order.information'
        ].sudo().create({
            'customer_id': customer.id,
            'order_line_lines': [
                (0, 0, {
                    'product_id': product.id,
                    'quantity': quantity,
                    'unit_price': product.selling_price,
                })
            ]
        })
        # =====================================================
        # REDIRECT TO SUCCESS PAGE
        # =====================================================
        return request.redirect(
            '/pottery/order/success/%s' % order.id
        )
    # =========================================================
    # ORDER SUCCESS PAGE
    # =========================================================
    @http.route(
        '/pottery/order/success/<int:order_id>',
        type='http',
        auth='public',
        website=True
    )
    def pottery_order_success(self, order_id):
        order = request.env[
            'customer.order.information'
        ].sudo().browse(order_id)
        if not order.exists():
            return request.not_found()
        return request.render(
            'pottery_artisan_production_management.website_order_success',
            {
                'order': order,
            }
        )
    # =========================================================
    # TRACK ORDER PAGE
    # =========================================================

    @http.route(
        '/pottery/track-order',
        type='http',
        auth='public',
        website=True
    )
    def pottery_track_order(self, **kwargs):
        return request.render(
            'pottery_artisan_production_management.website_track_order',
            {}
        )
    # =========================================================
    # TRACK ORDER SEARCH
    # =========================================================
    @http.route(
        '/pottery/track-order/search',
        type='http',
        auth='public',
        website=True,
        methods=['POST']
    )
    def pottery_track_order_search(self, **post):
        # =====================================================
        # GET FORM VALUES
        # =====================================================
        order_reference = post.get('order_reference')
        email = post.get('email')
        # =====================================================
        # VALIDATE INPUT
        # =====================================================
        if not order_reference or not email:
            return request.render(
                'pottery_artisan_production_management.website_track_order',
                {
                    'error': 'Please enter your Order Reference and Email.'
                }
            )
        # =====================================================
        # SEARCH ORDER
        # =====================================================
        order = request.env[
            'customer.order.information'
        ].sudo().search([
            ('name', '=', order_reference.strip()),
            ('customer_id.email', '=', email.strip()),
        ], limit=1)
        # =====================================================
        # ORDER NOT FOUND
        # =====================================================
        if not order:
            return request.render(
                'pottery_artisan_production_management.website_track_order',
                {
                    'error': 'Order not found. Please check your Order Reference and Email.'
                }
            )
        # =====================================================
        # GET LATEST DELIVERY
        # =====================================================

        delivery = request.env['delivery.information'].sudo().search([('order_id', '=', order.id),('status', '!=', 'cancelled')], order='delivery_date desc, id desc', limit=1)
        # =====================================================
        # ORDER FOUND
        # =====================================================
        return request.render('pottery_artisan_production_management.website_order_tracking_result',
            {
                'order': order,
                'delivery': delivery,
            }
        )
    # =========================================================
    # DOWNLOAD CUSTOMER ORDER REPORT
    # =========================================================
    @http.route(
        '/pottery/order/report/<int:order_id>',
        type='http',
        auth='public',
        website=True
    )
    def download_customer_order_report(self, order_id, **kwargs):
        # Get Order
        order = request.env[
            'customer.order.information'
        ].sudo().browse(order_id)
        # Validate Order
        if not order.exists():
            return request.not_found()
        # Generate PDF Report
        report = request.env.ref(
            'pottery_artisan_production_management.action_report_customer_order'
        )
        pdf_content, _ = report._render_qweb_pdf(
            report_ref=report.report_name,
            res_ids=[order.id]
        )
        # Download PDF
        filename = f'Order_{order.name}.pdf'
        return request.make_response(
            pdf_content,
            headers=[
                (
                    'Content-Type',
                    'application/pdf'
                ),
                (
                    'Content-Disposition',
                    f'attachment; filename="{filename}"'
                ),
            ]
        )
    # =========================================================
    # COLLECTION PAGE
    # =========================================================
    @http.route(
        '/pottery/collection',
        type='http',
        auth='public',
        website=True
    )
    def pottery_collection(self, **kwargs):
        products = request.env[
            'pottery.product.information'
        ].sudo().search([
            ('active', '=', True)
        ])
        return request.render(
            'pottery_artisan_production_management.website_collection',
            {
                'products': products,
            }
        )
    # =========================================================
    # OUR STORY PAGE
    # =========================================================
    @http.route(
        '/pottery/our-story',
        type='http',
        auth='public',
        website=True
    )
    def pottery_our_story(self, **kwargs):
        return request.render(
            'pottery_artisan_production_management.website_our_story',
            {}
        )
    # =========================================================
    # CONTACT PAGE
    # =========================================================
    @http.route(
        '/pottery/contact',
        type='http',
        auth='public',
        website=True
    )
    def pottery_contact(self, **kwargs):
        return request.render(
            'pottery_artisan_production_management.website_contact',
            {}
        )

    # =========================================================
    # CONTACT FORM - SEND EMAIL
    # =========================================================

    @http.route(
        '/pottery/contact/send',
        type='http',
        auth='public',
        website=True,
        methods=['POST']
    )
    def pottery_contact_send(self, **post):

        name = post.get('name')
        email = post.get('email')
        message = post.get('message')
        # Company email
        company = request.env.company
        if not company.email:
            return request.render(
                'pottery_artisan_production_management.website_contact',
                {
                    'error': 'Company email is not configured.'
                }
            )

        # Send email
        mail = request.env['mail.mail'].sudo().create({
            'subject': f'Website Contact Message from {name}',
            'email_from': email,
            'email_to': company.email,
            'body_html': f"""
                <h3>New Contact Message</h3>

                <p><strong>Name:</strong> {name}</p>

                <p><strong>Email:</strong> {email}</p>

                <p><strong>Message:</strong></p>

                <p>{message}</p>
            """,
        })

        mail.send()

        return request.render(
            'pottery_artisan_production_management.website_contact',
            {
                'success': 'Your message has been sent successfully!'
            }
        )