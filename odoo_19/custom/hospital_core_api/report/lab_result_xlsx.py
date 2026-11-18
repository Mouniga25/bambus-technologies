from odoo import models


class LabResultXlsx(models.AbstractModel):
    _name = 'report.hospital_core_api.lab_result_xlsx'
    _description = "Lab Result XLSX Report"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, docs):

        sheet = workbook.add_worksheet("Lab Result")

        # ==========================
        # Formats
        # ==========================
        title = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'bg_color': '#A076E5',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
        })

        header = workbook.add_format({
            'bold': True,
            'bg_color': '#A076E5',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'text_wrap': True,
        })

        normal = workbook.add_format({
            'border': 1,
            'text_wrap': True,
        })

        date_format = workbook.add_format({
            'border': 1,
            'num_format': 'dd-mm-yyyy',
        })

        # ==========================
        # Column Width
        # ==========================
        sheet.set_column('A:H', 20)

        row = 0

        # ==========================
        # Report Title
        # ==========================
        sheet.merge_range(row, 0, row, 7, "LAB RESULT REPORT", title)
        row += 2

        # ==========================
        # Headers
        # ==========================
        headers = [
            "Patient Name",
            "Doctor Name",
            "Test Name",
            "Result",
            "Unit",
            "Reference Range",
            "Status",
            "Test Date",
        ]

        for col, header_name in enumerate(headers):
            sheet.write(row, col, header_name, header)

        row += 1

        # ==========================
        # Data
        # ==========================
        for doc in docs:

            sheet.write(row, 0, doc.patient_id.name or "", normal)
            sheet.write(row, 1, doc.doctor_id.doctor_name or "", normal)
            sheet.write(row, 2, doc.test_name or "", normal)
            sheet.write(row, 3, doc.result or "", normal)
            sheet.write(row, 4, doc.unit or "", normal)
            sheet.write(row, 5, doc.reference_range or "", normal)
            sheet.write(row, 6, doc.amount_status or "", normal)

            if doc.test_date:
                sheet.write_datetime(row, 7, doc.test_date, date_format)
            else:
                sheet.write(row, 7, "", normal)

            row += 1