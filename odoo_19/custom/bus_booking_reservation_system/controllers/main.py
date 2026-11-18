from odoo import http
from odoo.http import request
from datetime import datetime


class BusBooking(http.Controller):

    @http.route('/bus/booking', auth='public', website=True)
    def booking_page(self, **kw):

        places = request.env['places.info'].sudo().search([])
        services = request.env['classof.service'].sudo().search([])

        return request.render(
            'bus_booking_reservation_system.bus_booking_page',
            {
                'places': places,
                'services': services,
            }
        )

    @http.route('/bus/booking/submit', auth='public', website=True, methods=['POST'], csrf=True)
    def booking_submit(self, **post):

        request.env['booking.forms'].sudo().create({
            'passenger_name': post.get('passenger_name'),
            'phone_number': post.get('phone_number'),
            'email': post.get('email'),
            'from_place_id': int(post.get('from_place_id')),
            'to_place_id': int(post.get('to_place_id')),
            'adults_male': int(post.get('adults_male', 0)),
            'adults_female': int(post.get('adults_female', 0)),
            'children_male': int(post.get('children_male', 0)),
            'children_female': int(post.get('children_female', 0)),
            'departure_date_time': post.get('departure_date_time'),
            'arrival_date_time': post.get('arrival_date_time'),
            'pickup_address': post.get('pickup_address'),
            'destination_address': post.get('destination_address'),
            'classof_service_id': int(post.get('classof_service_id')),
        })
        departure = datetime.strptime(post.get('departure_date_time'),"%Y-%m-%dT%H:%M")

        arrival = datetime.strptime(post.get('arrival_date_time'),"%Y-%m-%dT%H:%M")
        print("Departure:", departure)
        print("Arrival:", arrival)

    

        return request.redirect('/bus/booking')
    
    
    