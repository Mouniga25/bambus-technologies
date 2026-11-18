from odoo import models


class QualityXlsxReport(models.AbstractModel):
    _name = 'report.quality_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Quality XLSX Report'

    def generate_xlsx_report(self, workbook, data, qualities):

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
        })

        text_format = workbook.add_format({
            'font_size': 10,
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
        })

        number_format = workbook.add_format({
            'font_size': 10,
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '0.00',
        })

        pending_format = workbook.add_format({
            'font_size': 10,
            'bold': True,
            'font_color': '#B88732',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        approved_format = workbook.add_format({
            'font_size': 10,
            'bold': True,
            'font_color': '#198754',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        rejected_format = workbook.add_format({
            'font_size': 10,
            'bold': True,
            'font_color': '#A94442',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        # =========================================================
        # WORKSHEET
        # =========================================================

        sheet = workbook.add_worksheet('Quality Report')

        sheet.set_landscape()
        sheet.set_paper(9)

        sheet.fit_to_pages(1, 0)

        sheet.set_margins(
            left=0.3,
            right=0.3,
            top=0.5,
            bottom=0.5
        )

        # Column widths

        sheet.set_column('A:A', 18)
        sheet.set_column('B:B', 25)
        sheet.set_column('C:C', 22)
        sheet.set_column('D:D', 14)
        sheet.set_column('E:E', 14)
        sheet.set_column('F:F', 14)
        sheet.set_column('G:G', 16)

        # =========================================================
        # TITLE
        # =========================================================

        sheet.merge_range(
            'A1:G1',
            'QUALITY INSPECTION REPORT',
            title_format
        )

        sheet.set_row(0, 30)

        # =========================================================
        # HEADER
        # =========================================================

        headers = [
            'QC Ref',
            'Product',
            'Inspector',
            'Produced',
            'Passed',
            'Rejected',
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
        # DATA
        # =========================================================

        row = 3

        for quality in qualities:

            # QC Reference

            sheet.write(
                row,
                0,
                quality.name or '',
                text_format
            )

            # Product

            sheet.write(
                row,
                1,
                quality.product_id.display_name or '',
                text_format
            )

            # Inspector

            sheet.write(
                row,
                2,
                quality.inspector.name or '',
                text_format
            )

            # Produced

            sheet.write_number(
                row,
                3,
                quality.produced_qty or 0.0,
                number_format
            )

            # Passed

            sheet.write_number(
                row,
                4,
                quality.passed_qty or 0.0,
                number_format
            )

            # Rejected

            sheet.write_number(
                row,
                5,
                quality.rejected_qty or 0.0,
                number_format
            )

            # Status

            status_value = dict(
                quality._fields['status'].selection
            ).get(quality.status, '')

            if quality.status == 'pending':

                status_format = pending_format

            elif quality.status == 'approved':

                status_format = approved_format

            elif quality.status == 'rejected':

                status_format = rejected_format

            else:

                status_format = text_format

            sheet.write(
                row,
                6,
                status_value,
                status_format
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
                6
            )

        # =========================================================
        # FREEZE HEADER
        # =========================================================

        sheet.freeze_panes(3, 0)