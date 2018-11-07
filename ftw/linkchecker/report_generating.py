import xlsxwriter
from cell_format import BOLD, CENTER
import time


class ReportCreator(object):

    def __init__(self, xlsx_file_path):
        self.xlsx_file_path = xlsx_file_path
        self.row = 0
        self.workbook = xlsxwriter.Workbook(self.xlsx_file_path)
        self.worksheet = self.workbook.add_worksheet()
        self.autofitter_list_collector = []

    def append_report_data(self, report_data, format=None):
        format = format.get_workbook_format(self.workbook) if format else None

        for row_list in (report_data):
            col = 0
            for value in row_list:
                self.worksheet.write(self.row, col, value, format)
                col += 1
            self.row += 1
        self.autofitter_list_collector.append(report_data)

    def add_general_autofilter(self):
        self.worksheet.autofilter(0, 0, self.row, len(labels[0]) - 1)

    def cell_width_autofitter(self):
        flattened_list = [
            val for sublist in self.autofitter_list_collector for val in sublist]
        for i in range(0, len(flattened_list[0])):
            transposed = [x[i] if len(x) > i else '' for x in flattened_list]
            max_len = max(transposed, key=len)
            self.worksheet.set_column(self.row, i, len(max_len) + 7)

    def safe_workbook(self):
        self.workbook.close()


xlsx_file_path = 'Broken_Link_Report{}.xlsx'
xlsx_file_path = xlsx_file_path.format(time.strftime('_%Y_%m_%d_%H_%M'))

report_data = [
    ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
    ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
    ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
    ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
    ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
    ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
    ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
    ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
    ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
]

labels = [
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

file_i = ReportCreator(xlsx_file_path)
file_i.append_report_data(labels, BOLD & CENTER)
file_i.append_report_data(report_data)
file_i.add_general_autofilter()
file_i.cell_width_autofitter()
file_i.safe_workbook()
