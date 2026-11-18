from odoo import models


class KilnXlsxReport(models.AbstractModel):
    _name = 'report.pottery_artisan_production_management.kiln_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Kiln XLSX Report'

    def generate_xlsx_report(self, workbook, data, kilns):

        # =========================================================
        # FORMATS
        # =========================================================

        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_color': '#FFFFFF',
            'bg_color': '#1F4E5F',
            'align': 'center',
            'valign': 'vcenter',
        })

        header_format = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'font_color': '#FFFFFF',
            'bg_color': '#1F4E5F',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#D5DEE2',
        })

        text_format = workbook.add_format({
            'font_size': 10,
            'font_color': '#263238',
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#D5DEE2',
        })

        number_format = workbook.add_format({
            'font_size': 10,
            'font_color': '#263238',
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#D5DEE2',
            'num_format': '0.00',
        })

        count_format = workbook.add_format({
            'font_size': 10,
            'font_color': '#263238',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#D5DEE2',
            'num_format': '0',
        })

        available_format = workbook.add_format({
            'font_size': 10,
            'font_color': '#4F7D5A',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#D5DEE2',
        })

        busy_format = workbook.add_format({
            'font_size': 10,
            'font_color': '#B88732',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#D5DEE2',
        })

        maintenance_format = workbook.add_format({
            'font_size': 10,
            'font_color': '#A94442',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#D5DEE2',
        })

        inactive_format = workbook.add_format({
            'font_size': 10,
            'font_color': '#6B777C',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#D5DEE2',
        })

        # =========================================================
        # WORKSHEET
        # =========================================================

        sheet = workbook.add_worksheet('Kiln Report')

        sheet.set_landscape()
        sheet.set_paper(9)

        sheet.fit_to_pages(1, 0)

        sheet.set_margins(
            left=0.3,
            right=0.3,
            top=0.5,
            bottom=0.5
        )

        # Column Widths

        sheet.set_column('A:A', 25)
        sheet.set_column('B:B', 18)
        sheet.set_column('C:C', 22)
        sheet.set_column('D:D', 20)

        # =========================================================
        # REPORT TITLE
        # =========================================================

        sheet.merge_range(
            'A1:D1',
            'KILN MANAGEMENT REPORT',
            title_format
        )

        sheet.set_row(0, 30)

        # =========================================================
        # TABLE HEADER
        # =========================================================

        headers = [
            'Kiln',
            'Capacity',
            'Production Count',
            'Status',
        ]

        header_row = 2

        for column, header in enumerate(headers):

            sheet.write(
                header_row,
                column,
                header,
                header_format
            )

        sheet.set_row(header_row, 25)

        # =========================================================
        # KILN DATA
        # =========================================================

        row = 3

        for kiln in kilns:

            # -----------------------------------------------------
            # Kiln
            # -----------------------------------------------------

            sheet.write(
                row,
                0,
                kiln.kiln_code or kiln.name or '',
                text_format
            )

            # -----------------------------------------------------
            # Capacity
            # -----------------------------------------------------

            sheet.write_number(
                row,
                1,
                kiln.capacity or 0.0,
                number_format
            )

            # -----------------------------------------------------
            # Production Count
            # -----------------------------------------------------

            sheet.write_number(
                row,
                2,
                kiln.production_count or 0,
                count_format
            )

            # -----------------------------------------------------
            # Status
            # -----------------------------------------------------

            status_value = dict(
                kiln._fields['status'].selection
            ).get(kiln.status, '')

            if kiln.status == 'available':

                status_style = available_format

            elif kiln.status == 'in_use':

                status_style = busy_format

            elif kiln.status == 'maintenance':

                status_style = maintenance_format

            elif kiln.status == 'inactive':

                status_style = inactive_format

            else:

                status_style = text_format

            sheet.write(
                row,
                3,
                status_value,
                status_style
            )

            row += 1

        # =========================================================
        # FILTER
        # =========================================================

        if row > 3:

            sheet.autofilter(
                header_row,
                0,
                row - 1,
                3
            )

        # =========================================================
        # FREEZE HEADER
        # =========================================================

        sheet.freeze_panes(3, 0)