from odoo import models


class ProductionInformationXlsx(models.AbstractModel):

    _name = 'report.pottery_prod.production_information_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Production Information XLSX Report'

    def generate_xlsx_report(self, workbook, data, docs):

        sheet = workbook.add_worksheet("Production Report")

        # ============================================================
        # FORMATS
        # ============================================================

        # ----------------------------
        # TITLE
        # ----------------------------

        title = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'bg_color': '#6B1F3A',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
        })

        # ----------------------------
        # HEADER
        # ----------------------------

        header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'bg_color': '#6B1F3A',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
        })

        # ----------------------------
        # COMMON DATA FORMAT
        # ----------------------------

        data_format = workbook.add_format({
            'font_size': 10,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
        })

        # ----------------------------
        # NUMBER FORMAT
        # ----------------------------

        number_format = workbook.add_format({
            'font_size': 10,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': '0.00',
        })

        # ----------------------------
        # AMOUNT FORMAT
        # ----------------------------

        amount_format = workbook.add_format({
            'font_size': 10,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': '#,##0.00',
        })

        # ----------------------------
        # TOTAL PRODUCTION COST
        # ----------------------------

        total_cost_format = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'bg_color': '#FDF2E9',
            'font_color': '#6B1F3A',
            'border': 2,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': '#,##0.00',
        })

        # ============================================================
        # COLUMN WIDTHS
        # ============================================================

        sheet.set_column('A:A', 18)   # Production Reference
        sheet.set_column('B:B', 22)   # Artisan
        sheet.set_column('C:C', 20)   # Phone
        sheet.set_column('D:D', 20)   # Skill
        sheet.set_column('E:E', 14)   # Experience

        sheet.set_column('F:F', 25)   # Product
        sheet.set_column('G:G', 16)   # Production Date
        sheet.set_column('H:H', 16)   # Planned Quantity
        sheet.set_column('I:I', 18)   # Required Clay
        sheet.set_column('J:J', 20)   # Kiln
        sheet.set_column('K:K', 16)   # Status

        sheet.set_column('L:L', 16)   # Produced
        sheet.set_column('M:M', 16)   # Passed
        sheet.set_column('N:N', 16)   # Rejected
        sheet.set_column('O:O', 16)   # Wastage

        sheet.set_column('P:P', 18)   # Material Cost
        sheet.set_column('Q:Q', 18)   # Labour Cost
        sheet.set_column('R:R', 22)   # Total Production Cost

        # ============================================================
        # TITLE
        # ============================================================

        row = 0

        sheet.set_row(row, 30)

        sheet.merge_range(
            row,
            0,
            row,
            17,
            "PRODUCTION INFORMATION REPORT",
            title
        )

        row += 2

        # ============================================================
        # HEADERS
        # ============================================================

        headers = [
            "Production Reference",
            "Artisan",
            "Phone",
            "Skill",
            "Experience",
            "Product",
            "Production Date",
            "Planned Quantity",
            "Required Clay (KG)",
            "Kiln",
            "Status",
            "Produced Qty",
            "Passed Qty",
            "Rejected Qty",
            "Wastage (%)",
            "Material Cost",
            "Labour Cost",
            "Total Production Cost",
        ]

        sheet.set_row(row, 38)

        for col, header_name in enumerate(headers):

            sheet.write(
                row,
                col,
                header_name,
                header
            )

        row += 1

        # ============================================================
        # PRODUCTION RECORDS
        # ============================================================

        for doc in docs:

            # --------------------------------------------------------
            # STATUS
            # --------------------------------------------------------

            status = dict(
                doc._fields['status'].selection
            ).get(
                doc.status,
                doc.status or '-'
            )

            # --------------------------------------------------------
            # VALUES
            # --------------------------------------------------------

            values = [
                doc.name or '-',

                doc.artisan_id.display_name
                if doc.artisan_id
                else '-',

                doc.artisan_phone or '-',

                doc.artisan_skill or '-',

                doc.artisan_experience or 0,

                doc.product_id.display_name
                if doc.product_id
                else '-',

                doc.production_date or '-',

                doc.quantity or 0,

                doc.required_clay or 0,

                doc.kiln_id.display_name
                if doc.kiln_id
                else '-',

                status,

                doc.produced_qty or 0,

                doc.passed_qty or 0,

                doc.rejected_qty or 0,

                doc.wastage_percentage or 0,

                doc.material_cost or 0,

                doc.labour_cost or 0,

                doc.total_cost or 0,
            ]

            # --------------------------------------------------------
            # WRITE VALUES
            # --------------------------------------------------------

            for col, value in enumerate(values):

                # ----------------------------------------
                # TOTAL PRODUCTION COST
                # ----------------------------------------

                if col == 17:

                    sheet.write(
                        row,
                        col,
                        value,
                        total_cost_format
                    )

                # ----------------------------------------
                # MATERIAL / LABOUR COST
                # ----------------------------------------

                elif col in [15, 16]:

                    sheet.write(
                        row,
                        col,
                        value,
                        amount_format
                    )

                # ----------------------------------------
                # NUMERIC VALUES
                # ----------------------------------------

                elif col in [4, 7, 8, 11, 12, 13, 14]:

                    sheet.write(
                        row,
                        col,
                        value,
                        number_format
                    )

                # ----------------------------------------
                # ALL OTHER VALUES
                # ----------------------------------------

                else:

                    sheet.write(
                        row,
                        col,
                        value,
                        data_format
                    )

            # Row height
            sheet.set_row(row, 28)

            row += 1

        # ============================================================
        # FREEZE HEADER
        # ============================================================

        sheet.freeze_panes(3, 0)

        # ============================================================
        # FILTER
        # ============================================================

        if docs:

            sheet.autofilter(
                2,
                0,
                2 + len(docs),
                17
            )

        # ============================================================
        # PRINT SETTINGS
        # ============================================================

        sheet.set_landscape()

        sheet.fit_to_pages(1, 0)

        sheet.set_margins(
            left=0.25,
            right=0.25,
            top=0.50,
            bottom=0.50
        )

        # Repeat title + header rows while printing
        sheet.repeat_rows(0, 2)