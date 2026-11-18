from odoo import http
from odoo.http import request


class WebsiteCRMForm(http.Controller):

    @http.route(
        '/our-menu',
        type='http',
        auth='public',
        website=True
    )
    def our_menu(self):
        return request.render(
            'website_crm_form.our_menu_page'
        )
    @http.route(
        '/our-menu/submit',
        type='http',
        auth='public',
        website=True,
        methods=['POST'],
        csrf=True
    )
    def submit_form(self, **post):

        lead = request.env[
            'crm.lead'
        ].sudo().create({

            'name': post.get('subject'),
            'contact_name': post.get('name'),
            'email_from': post.get('email'),
            'phone': post.get('phone'),
            'description': post.get('message'),
        })
        return request.render(
            'website_crm_form.thank_you_page',
            {
                'enquiry_number': lead.enquiry_number,
            }
        )