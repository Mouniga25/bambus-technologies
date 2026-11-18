from odoo import models

class BookingListXlsx(models.AbstractModel):
    _name = "report.bus_booking_reservation_system_r.booking_list_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = 'sheet'

    def generate_xlsx_report(self, workbook, data, records):
        sheet = workbook.add_worksheet("Bookings")
        header = workbook.add_format({'bold': True})
        headers = [
            "Sequence",
            "Name",
            "Phone Number",
            "Email",
            "Total Passengers",
            "From Place",
            "To Place",
            "Departure Date",
            "Class Of Service",
            "State",
        ]
        for col, value in enumerate(headers):
            sheet.write(0, col, value, header)
        row = 1
        bookings = self.env['booking.info'].search([])
        for rec in records:
            sheet.write(row, 0, rec.name)
            sheet.write(row, 1, rec.passenger_name)
            sheet.write(row, 2, rec.phone_number)
            sheet.write(row, 3, rec.email)
            sheet.write(row, 4, rec.total_passenger)
            sheet.write(row, 5, rec.from_place_id.display_name)
            sheet.write(row, 6, rec.to_place_id.display_name)
            sheet.write(row, 7, str(rec.departure))
            sheet.write(row, 8, rec.class_of_service_id.display_name)

            state = dict(rec._fields['state'].selection).get(rec.state)
            sheet.write(row, 9, state)
            row += 1