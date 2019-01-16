import xlsxwriter

LABELS = [
    [
        'Internal/External',
        'Origin',
        'Destination',
        'Status Code',
        'Content Type',
        'Response Time',
        'Header Location',
        'Error Message'
    ]
]


class ReportCreator(object):

    def __init__(self, xlsx_file_path):
        self.xlsx_file_path = xlsx_file_path
        self.row = 0
        self.workbook = xlsxwriter.Workbook(self.xlsx_file_path)
        self.worksheet = self.workbook.add_worksheet()
        self.table = []

    def append_report_data(self, report_data, format=None):
        format = format.get_workbook_format(self.workbook) if format else None

        for row in report_data:
            for col, value in enumerate(row):
                self.worksheet.write(self.row, col, value, format)
            self.row += 1

        self.table.extend(report_data)

    def add_general_autofilter(self):
        self.worksheet.autofilter(0, 0, self.row, len(LABELS[0]) - 1)

    def get_column_widths(self):
        columns_size = [0] * len(self.table[0])
        for row in self.table:
            for j, column_element in enumerate(row):
                columns_size[j] = max(columns_size[j], len(column_element))
        return columns_size

    def cell_width_autofitter(self):
        column_widths = self.get_column_widths()
        for row, column_width in enumerate(column_widths):
            self.worksheet.set_column(self.row, row, column_width + 7)

    def safe_workbook(self):
        self.workbook.close()
