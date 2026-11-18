from odoo import models


class BusBookingXlsx(models.AbstractModel):

    _name = 'report.bus_booking_reservation_system.bus_booking_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, docs):

        sheet = workbook.add_worksheet("Bus Ticket")
        # ==========================
        # Formats
        # ==========================
        title = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'bg_color': '#A076E5',
            'font_color': 'white',
            'align': 'center'
        })
        header = workbook.add_format({
            'bold': True,
            'bg_color': '#A076E5',
            'font_color': 'white',
            'border': 1,
            'text_wrap': True,
            'align': 'center'
        })
        normal = workbook.add_format({
            'border': 1,
            'text_wrap': True
        })
        amount = workbook.add_format({
            'border': 1,
            'num_format': '₹ #,##0.00'
        })
        # ==========================
        # Column Width
        # ==========================
        sheet.set_column('A:N', 20)
        sheet.set_column('F:G', 25)
        sheet.set_column('L:L', 35)
        sheet.set_column('N:N', 18)
        row = 0
        # ==========================
        # Title (Only Once)
        # ==========================
        sheet.merge_range(
            row,
            0,
            row,
            13,
            "BUS BOOKING TICKET",
            title
        )
        row += 2
        # ==========================
        # Table Header (Only Once)
        # ==========================

        headers = [
            "Name",
            "Phone Number",
            "E-mail",
            "From Place",
            "To Place",
            "Departure Date/Time",
            "Arrival Date/Time",
            "Total Passengers",
            "Departure",
            "Arrival",
            "Boarding Point",
            "Pickup Address",
            "Service Class",
            "Total Amount",
        ]
        for col, name in enumerate(headers):

            sheet.write(
                row,
                col,
                name,
                header
            )
        row += 1
        # ==========================
        # Records
        # ==========================
        for doc in docs:
            values = [
                doc.passenger_name,
                doc.phone_number,
                doc.email,
                doc.from_place_id.place_name,
                doc.to_place_id.place_name,
                doc.departure_date_time,
                doc.arrival_date_time,
                doc.total_passengers,
                doc.from_place_id.place_name,
                doc.to_place_id.place_name,
                doc.boarding_points_id.place_name,
                doc.pickup_address,
                doc.classof_service_id.service_name,
                doc.total_amount,
            ]
            for col, value in enumerate(values):

                if col == 13:

                    sheet.write(
                        row,
                        col,
                        value or 0,
                        amount
                    )

                else:

                    sheet.write(
                        row,
                        col,
                        value or "",
                        normal
                    )


            row += 1