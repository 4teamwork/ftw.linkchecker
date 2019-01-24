from ftw.linkchecker.command import broken_link
import xlsxwriter

LABELS = broken_link.BrokenLink()
LABELS.is_internal = 'Internal/External'
LABELS.link_origin = 'Origin'
LABELS.link_target = 'Destination'
LABELS.status_code = 'Status Code'
LABELS.content_type = 'Content Type'
LABELS.response_time = 'Response Time'
LABELS.header_location = 'Header Location'
LABELS.error_message = 'Error Message'
LABELS = [LABELS]

NUMBER_OF_LABELS = 8


class ReportCreator(object):

    def __init__(self, xlsx_file_path):
        self.xlsx_file_path = xlsx_file_path
        self.row = 0
        self.workbook = xlsxwriter.Workbook(self.xlsx_file_path)
        self.worksheet = self.workbook.add_worksheet()
        self.table = []

    def append_report_data(self, link_objs, format=None):
        format = format.get_workbook_format(self.workbook) if format else None
        for link_obj in link_objs:

            int_ext_link = link_obj.is_internal
            if link_obj.is_internal is None:
                int_ext_link = 'Unknown'
            elif link_obj.is_internal is True:
                int_ext_link = 'Internal Link'
            elif link_obj.is_internal is False:
                int_ext_link = 'External Link'

            self.worksheet.write(self.row, 0, int_ext_link, format)
            self.worksheet.write(self.row, 1, str(link_obj.link_origin), format)
            self.worksheet.write(self.row, 2, str(link_obj.link_target), format)
            self.worksheet.write(self.row, 3, str(link_obj.status_code), format)
            self.worksheet.write(self.row, 4, str(link_obj.content_type), format)
            self.worksheet.write(self.row, 5, str(link_obj.response_time), format)
            self.worksheet.write(self.row, 6, str(link_obj.header_location), format)
            self.worksheet.write(self.row, 7, str(link_obj.error_message), format)

            self.row += 1
        self.table.extend(link_objs)

    def add_general_autofilter(self):
        self.worksheet.autofilter(0, 0, self.row, NUMBER_OF_LABELS - 1)

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
